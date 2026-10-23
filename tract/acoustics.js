// THE TUBE. Sound in a vocal tract is two pressure waves, one running toward the lips and one back, in a pipe whose
// cross-section changes along its length. Cut the pipe into short sections of constant area and everything that
// happens to the waves happens at the JOINTS between sections -- part goes on, part comes back, by how much the area
// changes -- while inside a section a wave just travels. Make a section exactly as long as sound travels in half a
// sample and "travels" is "moves along one slot of an array". That is the whole synthesiser (Kelly & Lochbaum, 1962),
// and nothing in it is a formant: resonances are what a pipe of that shape does.
//
// WHAT IS PHYSICAL HERE, beyond the textbook version (units are cgs: cm, g, s, dyn/cm2):
//   - A JOINT WHERE THE PIPE WIDENS LOSES PRESSURE. Air leaving a narrow place as a jet does not give its speed back
//     as pressure (Borda-Carnot): dp = rho/2 * U|U| * (1/A_narrow - 1/A_wide)^2. With that one term a constriction
//     holds pressure behind it, the flow through it falls, and a closure that opens discharges -- which is what a
//     fricative, a voiced stop's dying voice bar and a burst ARE. It costs one square root per joint.
//   - THE GLOTTIS IS SUCH A JOINT, with the lungs' pressure on one side and an area that the folds open and close.
//     The flow is solved against the wave coming back down the tract every sample, so the pulse is skewed by the
//     tract's inertia and F1 is damped while the folds stand open: source-tract interaction, not added, just there.
//   - TURBULENCE is made where a jet is: noise whose strength grows with the square of the Reynolds number past a
//     critical value, injected just downstream of the narrowest place (and at the glottis: aspiration).
//   - THE NOSE is a second pipe joined at the velum by a three-way joint whose third area is the velar port.
//   - THE WALLS GIVE. Cheeks and pharynx are flesh: at low frequencies they move with the pressure instead of
//     reflecting it, which is why no vowel's F1 goes below ~200Hz however closed the mouth is, and why a voice bar
//     hums at that pitch. Three lumped mass-and-friction branches along the pipe (their size follows the pipe's own
//     wall area) do it; without them an /i/ comes out at 160Hz.
//   - LENGTH: a section is c/(2 fs) long, 0.36cm at 48kHz, so the array is a whole number of them -- but a tract's
//     length changes as it speaks (lips pushed out, larynx lowered, jaw dropped). Both ends of a tract happen to be
//     UNIFORM tubes, the lip tube and the tube over the folds, and a uniform tube is nothing but a delay: so each
//     end is a fractional delay line of whatever length is needed, and the array between them never changes size.
// No imports, no DOM: the same class runs in an AudioWorklet and in a plain loop.

export const AIR = { c: 35000, rho: 0.00114, mu: 0.000186 };

export const ACOUSTICS = {                       // every number the tube uses, by name (the lab edits this object)
  wallLoss: 0.0032,            // per section: fraction of the FLOW lost to friction at the walls, x sqrt(1cm2 / area) (narrow places lose more).
  // ...and the friction and the heat the walls take GROW WITH FREQUENCY (with its square root): without that the upper resonances are
  // needle-sharp (F3 and F4 60-80 Hz wide where a mouth's are 100-250) and the top of the voice rings like a pipe. wallLossHigh is the
  // extra loss well above wallLossCornerHz; below the corner it fades out, so closures hold their pressure as before.
  wallLossHigh: .02, wallLossCornerHz: 3000,
                               // Flow, not pressure: a shut mouth must be able to HOLD pressure, or no stop ever builds up to its burst
  minArea: 0.0008,             // cm2: below this a section is shut (a rigid wall)
  bernoulli: 1.0,              // x the Borda-Carnot loss at a widening joint (0 = the lossless textbook joint)
  slitWidth: 2.5,              // cm: a nearly shut place is a SLIT this wide, and air creeps through a slit against friction
                               // (12 mu L w^2 / A^3): it is what stops a release being an explosion in its first millisecond
  lips: { reflect: 0.97, cornerK: 0.55 },     // reflection at the open end; its low-pass corner = cornerK * c / (2 pi r_lip)
  nostril: { reflect: 0.93, cornerK: 0.55, area: 0.55 },
  // turbulence at a supraglottal jet. A jet that strikes the TEETH a little way downstream is a far better noise maker
  // than one that only scrapes a wall (that is what makes s and sh sibilants, and f and th and x not): `wall` is the
  // efficiency without that obstacle, `teethReach` how far upstream of the teeth (cm) a jet still hits them
  noise: { reCrit: 1400, gain: 4.5e-6, lowHz: 900, highHz: 4500, spread: 2, maxArea: .8, wall: .14, teethReach: [0.8, 3.2], teethFull: 1.6, lipGain: .5, buildUp: .03, knee: 2.5e7 },   // lowHz..highHz: the band turbulence has its energy in; lipGain: a jet AT the lips radiates straight out (flow per unit of noise pressure)
  aspiration: { reCrit: 1200, gain: 5e-9 },                                    // ...and at the glottis
  glottis: { k: 1.1, length: 1.4, thickness: 0.3 },   // orifice coefficient; fold length and thickness, cm (viscous term)
  // `radiate`: how much of the walls' own movement is heard. Throat and cheeks are skin: what they take from the pipe they
  // give, dully, to the air outside -- which is ALL there is to hear of a /b d g/ while the mouth is shut (the voice bar)
  walls: { mass: 1.5, resistance: 1400, stiffness: 3e5, at: [0.2, 0.5, 0.8], radiate: 1, radiateAboveHz: 70 },   // g/cm2, g/(cm2 s), dyn/cm3 of yielding wall (Ishizaka et al. 1975), lumped at these fractions of the length
  radiation: 1.0,              // output gain on d/dt of the flow leaving lips + nostrils
  areaSmoothMs: 5,             // areas glide to their new values over this long (no zipper noise)
  // ...and NO SECTION CHANGES SIZE FASTER THAN THIS (cm2 per ms, x the head's area), however far its new value is. The mouth's own
  // limits are enforced on the ORGANS (planner LIMITS); this is the same thing said about the pipe, and it is the last guard against
  // a single frame of nonsense -- a closure whose section jumps while it is holding the lungs' pressure is a bang, not a release.
  // A stop's release opens its constriction at about .05-.2 cm2/ms, so this is far above anything real.
  areaRate: 1.6,
  // ...and no section more than DOUBLES in this long. Near a closure the area is tiny and its RATE means little: what matters is the
  // ratio, because that is what the waves see. Letting a shut section grow by six times in a third of a millisecond is a bang rather
  // than a burst -- and the smaller the head, the shorter the cavity in front and the louder that bang (a woman's /d/ in "old dog"
  // came out at 54% of her loudest vowel where a man's was 17%). A stop's burst wants about 5 ms.
  areaDoubleMs: 0.45,
  // A TRILL IS NOT A MOVEMENT THE SPEAKER MAKES: the tip is held lightly against the ridge and the AIR beats it. The tip is a
  // sprung mass (its own frequency `hz`, `damping`), pressed shut a little (`preload`, in rest openings); the pressure across the
  // closure pushes it open (`push`: openings per 8 cm H2O), and once air streams through, the pressure in the gap falls by
  // 1/2 rho v2 (`bernoulli`) and the spring brings it back -- so how fast it beats, whether it starts at all and when it stalls
  // depend on the breath and on how firmly it is held. `reach`: sections near the tip narrower than this (cm2) move with it.
  // THE PIRIFORM SINUSES: two blind pockets beside the larynx tube, opening into the throat at its top. A closed side branch takes
  // the sound at the frequency where it is a quarter wave long -- a dip at 4-5 kHz in every voice (higher in a shorter throat), part
  // of what makes a voice sound like a throat and not like a pipe. length cm (both taken as one), area cm2 (the two together),
  // reflect: what comes back from the closed end. area 0: none.
  piriform: { length: 1.9, area: 1.3, reflect: .94 },
  // THE TRACHEA UNDER THE FOLDS. Without it the lungs are an ideal pressure source and there is nothing below the glottis to ring;
  // with it the air column under the folds is a tube of its own, heard whenever they are open -- through the open half of every
  // cycle, and all the way through an /h/ or a breathy voice. Its far end opens into the lungs, which is nearly a pressure NODE
  // (`lungR`: the bronchial tree's resistance there, x this tube's own impedance -- small), so its resonances are the quarter-wave
  // ones: c/4L = 515, 1545, 2575 Hz for 17 cm. `loss` per pass and `lp` (how much of each pass goes through a one-pole low-pass)
  // are the soft walls down there: without them the resonances are needles, where a real trachea's are 100-300 Hz wide.
  // area: 0 takes it away and leaves the ideal source that was there before.
  subglottal: { area: 2.5, length: 17, lungR: .13, loss: .92, lp: .35 },
  // THE PARANASAL SINUSES: rooms of air beside the nose, each joined to it by one narrow ostium -- a mass of air in the neck over the
  // room's springiness, which is a Helmholtz resonator. At its own frequency it swallows what passes the opening, leaving a ZERO in
  // the nose's output (and a pole just below it): it is what makes a nasal murmur ragged instead of smooth, and it is the part of a
  // head that differs most from person to person. volume cm3, ostium cm2, neck cm, `at`: where along the nose it opens (0 the velum,
  // 1 the nostrils), damp: its own damping ratio (the bandwidth of the zero). f = (c/2pi) sqrt(ostium / (volume * neck)).
  // the closed rooms that hang off the mouth itself: the one under a raised tongue blade (anatomy.sublingual says how big it is at
  // each moment) and the pocket a lateral leaves behind its closure. Both are delays there and back, reflected at the dead end.
  // openMs: the room under the tongue is SEALED by the contact that shuts the mouth -- at once, as flesh does -- and opens again only
  // as the tongue changes shape, which is slow. Let it open at the tube's own rate and it ramps in while a stop's burst is still
  // ringing, which turns the burst into a bang (and whether it does depends on the head, so one voice clicked and another did not).
  sublingual: { reflect: .96, openMs: 30 }, lateralPocket: { reflect: .94 },
  // THE FOUR PARANASAL PAIRS, each as its own Helmholtz resonator: a room of air (volume, ml) breathing
  // through its ostium (cm2) down a neck (cm), hanging off the nose where it really drains into it (`at`: 0
  // the velum, 1 the nostrils). Each puts a ZERO in the nose at its own frequency, f = (c/2pi)*sqrt(A/(V*L)),
  // and it is the spread of those zeros between 400 and 1100 Hz that makes a nasal sound like a head rather
  // than a pipe. They were two before -- the maxillary pair, and the frontal and ethmoid lumped as one.
  sinuses: [{ at: .10, volume: 7.5, ostium: .04, neck: .45, damp: .14 },    // sphenoid: the hindmost, into the sphenoethmoidal recess -- ~606 Hz
             { at: .28, volume: 15, ostium: .05, neck: .5, damp: .12 },     // maxillary: the big pair, under the cheeks, into the middle meatus -- ~455 Hz
             { at: .42, volume: 5.5, ostium: .055, neck: .3, damp: .18 },   // ethmoid: the honeycomb of cells between the eyes, as one -- ~1017 Hz
             { at: .58, volume: 7, ostium: .066, neck: .6, damp: .15 }],    // frontal: over the brow, down the frontonasal duct -- ~698 Hz
  flap: { hz: 26, damping: .22, preload: .4, push: 5, bernoulli: 1, reach: .6 },
};

// the nasal tract's area function from the velum to the nostrils, cm2 (after Dang & Honda 1994, smoothed), 11.5cm
export const NOSE_AREAS = [0.6, 1.1, 1.9, 2.6, 3.1, 3.4, 3.3, 3.0, 2.6, 2.3, 2.0, 1.7, 1.4, 1.1, 0.8, 0.6, 0.5];
export const NOSE_LENGTH = 11.5;

const solveU = (D, Zs, a) => a < 1e-12 ? D / Zs : (D >= 0 ? 2 * D / (Zs + Math.sqrt(Zs * Zs + 4 * a * D)) : 2 * D / (Zs + Math.sqrt(Zs * Zs - 4 * a * D)));

export class Tube {
  // fs: output rate. lengthCm: the SHORTEST the tract will be (the rest is the lip-end delay). cfg: ACOUSTICS
  // head: the speaker's scale (anatomy.scale) -- the nose, the walls and the piriform sinuses belong to the head too, and a smaller head
  // has a shorter nose (its resonances and a nasal's zeros higher), less and thinner wall (the floor under F1 higher) and shorter sinuses
  constructor(fs, lengthCm, cfg = ACOUSTICS, seed = 1, head = { oral: 1, pharynx: 1 }) {
    this.fs = fs; this.cfg = cfg; this.dx = AIR.c / (2 * fs);
    const hs = Math.sqrt(head.oral * head.pharynx); this.head = { oral: head.oral, pharynx: head.pharynx, mean: hs, area: hs * hs };
    this.N = Math.max(8, Math.floor(lengthCm / this.dx));
    const N = this.N;
    this.A = new Float64Array(N).fill(3); this.At = new Float64Array(N).fill(3);      // areas now, and where they are going
    this.R = new Float64Array(N); this.L = new Float64Array(N); this.nR = new Float64Array(N); this.nL = new Float64Array(N); this.dLP = new Float64Array(N);   // (dLP: each section's flow wave, low-passed -- what the frequency-dependent loss leaves alone)
    this.M = Math.max(4, Math.round(NOSE_LENGTH * head.oral / this.dx));
    const M = this.M;
    this.nA = new Float64Array(M); for (let i = 0; i < M; i++) { const u = i / (M - 1) * (NOSE_AREAS.length - 1), k = Math.floor(u), f = u - k; this.nA[i] = (NOSE_AREAS[k] * (1 - f) + (NOSE_AREAS[Math.min(k + 1, NOSE_AREAS.length - 1)]) * f) * this.head.area * (head.nose ?? 1); }
    this.nRr = new Float64Array(M); this.nLl = new Float64Array(M); this.nnR = new Float64Array(M); this.nnL = new Float64Array(M);
    this.teethAt = N - 3; this.velumAt = Math.round(N * 0.48); this.velum = 0; this.velumT = 0; this.noseLive = 0;
    this.flapOn = 0; this.flapAt = N - 4; this.flapS = 1; this.flapV = 0;      // the sprung tip: how far it is engaged (0..1, set by the owner), where, its opening (x rest) and speed
    this.lipExtra = 0; this.lipExtraT = 0; this.dl = new Float64Array(32); this.dr = new Float64Array(32); this.dp = 0;   // the lip-end delay lines (out and back)
    this.gloExtra = 0; this.gloExtraT = 0; this.gu = new Float64Array(32); this.gd = new Float64Array(32);                  // ...and the glottis end's (up and down)
    this.lipLP = 0; this.nosLP = 0; this.uPrev = 0; this.seed = seed >>> 0 || 1;
    this.noiseLP = 0; this.noiseHP = 0; this.U0 = 0; this.Uc = 0; this.narrow = 0;
    this.meter = { Ug: 0, Pm: 0, noise: 0 };
    this.wallAt = cfg.walls.at.map((u) => Math.min(N - 2, Math.max(1, Math.round(u * N)))); this.wallU = new Float64Array(this.wallAt.length); this.wallX = new Float64Array(this.wallAt.length); this.wallS = 100 * this.head.area;
    { const P = cfg.piriform ?? { area: 0 }; this.pirA = P.area * this.head.area; this.pirD = Math.max(1.5, Math.min(60, 2 * (P.length ?? 1.9) * head.pharynx / this.dx)); this.pirAt = 1; this.pb = new Float64Array(64); this.pp = 0; }
    { const S = cfg.subglottal ?? { area: 0 }; this.subA = (S.area ?? 0) * this.head.area; this.subD = Math.max(2, Math.min(250, (S.length ?? 17) * this.head.pharynx / this.dx));
      this.su = new Float64Array(256); this.sd = new Float64Array(256); this.sp = 0; this.subLP = 0; }      // the trachea: the wave going up to the folds, and the one coming back down
    this.sublA = 0; this.sublAT = 0; this.sublD = 2; this.sublDT = 2; this.sublAt = N - 6; this.slb = new Float64Array(64); this.slp = 0;   // the room under the tongue
    this.latA = 0; this.latAT = 0; this.latD = 4; this.latDT = 4; this.latAt = N - 8; this.latBt = N - 5; this.lfw = new Float64Array(64); this.lbw = new Float64Array(64); this.lpp = 0;   // ...and the road round a lateral
    // the sinuses: one mass-and-spring each, hanging off a section of the nose (the room and its ostium scale with the head)
    this.sin = (cfg.sinuses ?? []).map((S) => { const V = S.volume * this.head.area * this.head.mean, os = S.ostium * this.head.area, nk = S.neck * this.head.mean;
      const Mm = AIR.rho * nk / Math.max(1e-4, os), Cc = V / (AIR.rho * AIR.c * AIR.c);
      return { at: Math.min(M - 2, Math.max(0, Math.round(S.at * (M - 1)))), M: Mm, C: Cc, R: (S.damp ?? .12) * 2 * Math.sqrt(Mm / Cc), U: 0, X: 0 }; });
  }
  // A CLOSED ROOM OFF THE TRACT (the room under the tongue, the dead end behind a lateral's closure): a three-way joint and a pipe
  // there and back. The same thing the piriform sinuses are, but its size and its length change as the mouth moves, so both are glided.
  // `buf` holds what is travelling in it; `D` is there and back in half-samples. Returns the joint's pressure (0 if nothing was done).
  room(i, area, D, buf, pt, ref, R, L, nR, nL, minA) {
    const A = this.A, rc = AIR.rho * AIR.c, k = Math.floor(D), f = D - k, n = buf.length;
    const back = buf[(pt - k + 2 * n) % n] * (1 - f) + buf[(pt - k - 1 + 2 * n) % n] * f;
    const Al = A[i], Ar = A[i + 1];
    if (Al < minA || Ar < minA) { buf[pt] = back * ref; return 0; }                    // (shut on one side: the room only rings on)
    const Y1 = Al / rc, Y2 = Ar / rc, Y3 = area / rc, p = 2 * (Y1 * R[i] + Y2 * L[i + 1] + Y3 * back) / (Y1 + Y2 + Y3);
    nL[i] = p - R[i]; nR[i + 1] = p - L[i + 1]; buf[pt] = (p - back) * ref; return p;
  }
  rnd() { let s = this.seed; s ^= s << 13; s ^= s >>> 17; s ^= s << 5; this.seed = s >>> 0; return (this.seed / 4294967296) * 2 - 1; }
  // set where the shape is going: areas (length N, cm2), velar port (cm2), extra length at the lips (cm)
  shape(areas, velum = 0, lipExtraCm = 0, gloExtraCm = 0) { this.At.set(areas); this.gloExtraT = Math.max(0, Math.min(28, gloExtraCm / this.dx));
    let S = 0; for (let i = 0; i < this.N; i++) S += 2 * Math.sqrt(Math.PI * Math.max(areas[i], .05)) * this.dx; this.wallS = S;   // the wall's area, for the yielding branches
    this.velumT = velum; this.lipExtraT = Math.max(0, Math.min(28, lipExtraCm / this.dx)); }
  snap() { this.A.set(this.At); this.velum = this.velumT; this.lipExtra = this.lipExtraT; this.gloExtra = this.gloExtraT; }
  reset() { for (const a of [this.R, this.L, this.nR, this.nL, this.nRr, this.nLl, this.nnR, this.nnL, this.dl, this.dr, this.gu, this.gd, this.su, this.sd, this.slb, this.lfw, this.lbw, this.wallU, this.wallX, this.pb, this.dLP]) a.fill(0);
    for (const S of this.sin) { S.U = 0; S.X = 0; } this.lipLP = this.nosLP = this.uPrev = this.yPrev = this.noiseLP = this.noiseHP = 0; this.noseLive = 0; }

  // one output sample. g: { Ps: lung pressure dyn/cm2, Ag: glottal area cm2 }   inject: an impulse for measuring
  step(g, inject = 0) {
    const c = this.cfg, N = this.N, A = this.A, At = this.At, rc = AIR.rho * AIR.c, halfRho = AIR.rho / 2 * c.bernoulli;
    const glide = 1 / Math.max(1, c.areaSmoothMs * .001 * this.fs), minArea = c.minArea, minA = c.minArea;
    // A SECTION THAT CHANGES SIZE KEEPS ITS PRESSURE AND ITS FLOW, not its two waves. The waves are a way of writing
    // pressure (R+L) and flow ((R-L) A / rho c); in a narrow place with air streaming through it they are huge and
    // nearly cancel (+36000 and -34000 inside a /k/ for a pressure of 2000), so changing A under them unchanged
    // invents flow -- hundreds of dyn/cm2 of it per sample -- and every constriction that moved while air was passing
    // clicked. The difference R-L is rescaled by old area / new area; the sum is left alone.
    let fk = -9, fm = 1;
    if (this.flapOn > .01 || Math.abs(this.flapS - 1) > .01) { const F = c.flap, k = Math.max(1, Math.min(N - 2, this.flapAt)), w = 2 * Math.PI * F.hz, h = 1 / this.fs, a = Math.max(A[k], .02);
      const v = (this.R[k] - this.L[k]) * A[k] / rc / a, up = At[k - 1] < F.reach ? Math.max(0, k - 2) : k - 1, dn = At[k + 1] < F.reach ? Math.min(N - 1, k + 2) : k + 1,      // (the air that pushes is the air BEHIND everything that moves with the tip)
        drive = (this.R[up] + this.L[up]) - (this.R[dn] + this.L[dn]) - F.bernoulli * AIR.rho / 2 * v * v;
      const on = Math.min(1, this.flapOn), rest = 1 - on * (1 + F.preload), sp = this.flapS;
      this.flapV += (w * w * (rest - sp + on * F.push * Math.max(-1.5, Math.min(1.5, drive / 7845))) - 2 * F.damping * (sp < 0 ? 4 : 1) * w * this.flapV) * h;
      this.flapS = Math.max(-1, Math.min(3, sp + this.flapV * h)); fk = k; fm = Math.max(0, this.flapS); }
    const maxStep = (c.areaRate ?? 1e9) * this.head.area * 1000 / this.fs, grow = Math.pow(2, 1000 / ((c.areaDoubleMs ?? 1e-9) * this.fs));
    for (let i = 0; i < N; i++) { const a0 = A[i], tgt = i >= fk - 1 && i <= fk + 1 && At[i] < c.flap.reach ? At[i] * fm : At[i];
      let a1 = a0 + Math.max(-maxStep, Math.min(maxStep, (tgt - a0) * glide));
      if (a1 > a0 * grow && a0 > 0) a1 = Math.min(a1, Math.max(a0 * grow, a0 + minArea));      // (...and never more than doubling in `areaDoubleMs`)
      if (a1 !== a0) { const k = Math.max(a0, 1e-4) / Math.max(a1, 1e-4), p = this.R[i] + this.L[i], d = (this.R[i] - this.L[i]) * k; this.R[i] = (p + d) / 2; this.L[i] = (p - d) / 2; this.dLP[i] *= k; A[i] = a1; } }
    this.velum += (this.velumT - this.velum) * glide; this.lipExtra += (this.lipExtraT - this.lipExtra) * glide; this.gloExtra += (this.gloExtraT - this.gloExtra) * glide;
    { const g = this.sublAT < this.sublA ? glide : 1 / Math.max(1, (c.sublingual.openMs ?? c.areaSmoothMs) * .001 * this.fs);      // shut at once, open slowly
      this.sublA += (this.sublAT - this.sublA) * g; this.sublD += (this.sublDT - this.sublD) * g; }      // (a branch that appeared in one frame would take a joint's flow with it: a click)
    this.latA += (this.latAT - this.latA) * glide; this.latD += (this.latDT - this.latD) * glide;
    const nz = c.noise;
    let out = 0;
    for (let half = 0; half < 2; half++) {
      const R = this.R, L = this.L, nR = this.nR, nL = this.nL;
      // ---- the glottis: lungs at Ps behind an orifice of area Ag
      {
        // THE TUBE OVER THE FOLDS HAS ITS OWN WIDTH. The stretch below the array (a delay, so that the tract's length can change smoothly) used
        // to be taken as wide as the array's first section -- so the narrow larynx tube, which is what gathers a voice's energy near 3 kHz
        // (its "ring"), was not there. It is a pipe of area larynxArea now, meeting section 0 at a joint like any other.
        const aL = Math.max(this.larynxArea ?? A[0], minA), Z0 = rc / aL, Ag = g.Ag, n = 32;
        this.dp = (this.dp + 1) % n;                                       // (one clock for all four delay lines)
        const e = this.gloExtra, k = Math.floor(e), f = e - k, at = (j) => (this.dp - j + 2 * n) % n;
        const Zr = rc / Math.max(A[0], minA), Rin = this.gu[at(k)] * (1 - f) + this.gu[at(k + 1)] * f, Uj = 2 * (Rin - L[0]) / (Z0 + Zr);   // the joint at the top of the larynx tube
        this.gd[this.dp] = Rin - Z0 * Uj; const Lg = this.gd[at(k)] * (1 - f) + this.gd[at(k + 1)] * f;   // the wave coming down, after the tube over the folds
        // ---- the trachea: what the folds see BELOW them. The lungs sit at the far end as a pressure source behind `lungR`; what
        // comes back up from them is the tube's own ringing. With no trachea (area 0) this is just the lung pressure, as before.
        let Psub = g.Ps, Zs = 0, xUp = 0;
        if (this.subA > 0) { const S = c.subglottal, D = this.subD, ks = Math.floor(D), fs2 = D - ks, n2 = 256;
          const at2 = (j) => (this.sp - j + 2 * n2) % n2;
          this.sp = (this.sp + 1) % n2;
          xUp = this.su[at2(ks)] * (1 - fs2) + this.su[at2(ks + 1)] * fs2;                    // what left the lungs a tube's length ago
          const down = this.sd[at2(ks)] * (1 - fs2) + this.sd[at2(ks + 1)] * fs2;             // ...and what reached them from the folds
          const rt = S.lungR ?? .13, r = (rt - 1) / (rt + 1), lp = Math.max(0, Math.min(.95, S.lp ?? 0));
          this.subLP += (down - this.subLP) * (1 - lp);
          this.su[this.sp] = ((r * (down * (1 - lp) + this.subLP * lp)) + g.Ps / (1 + rt)) * (S.loss ?? 1);
          Zs = rc / this.subA; Psub = 2 * xUp;
        }
        let U = 0;
        if (Ag > 1e-5) {
          const G = c.glottis, a = c.glottis.k * AIR.rho / (2 * Ag * Ag), Rv = 12 * AIR.mu * G.length * G.length * G.thickness / (Ag * Ag * Ag);
          U = solveU(Psub - 2 * Lg, Z0 + Zs + Rv, a);
          const Re = 2 * AIR.rho * Math.abs(U) / (AIR.mu * G.length), over = Re * Re - c.aspiration.reCrit * c.aspiration.reCrit;
          if (over > 0) U += this.rnd() * over * c.aspiration.gain * (this.breathNoise ?? 1) * Math.sqrt(Ag) * 60;      // (breathNoise: x, one speaker's -- set by whoever owns the voice)
        }
        if (this.subA > 0) this.sd[this.sp] = xUp - Zs * U;                                  // and what the folds send back down
        this.gu[this.dp] = Lg + Z0 * U + inject; nR[0] = L[0] + Zr * Uj; this.U0 = U;
      }
      inject = 0;
      // ---- the joints along the mouth
      let lipNoise = 0;
      for (let i = 0; i + 1 < N; i++) {
        const Al = A[i], Ar = A[i + 1];
        if (i === this.velumAt && this.velum > 1e-4) continue;           // (the three-way joint below)
        if (i === this.pirAt && this.pirA > 0 && Al >= .3 && Ar >= .3) continue;   // (and the sinuses')
        if (this.sublA > 1e-4 && i === this.sublAt) continue;              // (and the room under the tongue's, and the lateral's dead end)
        if (this.latA > 1e-4 && i === this.latAt) continue;
        if (Al < minA || Ar < minA) { nL[i] = R[i]; nR[i + 1] = L[i + 1]; continue; }   // shut: both sides see a wall
        const Zl = rc / Al, Zr = rc / Ar, D = 2 * (R[i] - L[i + 1]);
        const d = 1 / Al - 1 / Ar, a = halfRho * d * d;                   // a jet forms whichever way the air is going, where the pipe widens
        const An = Al < Ar ? Al : Ar, Rv = An < .2 ? 12 * AIR.mu * this.dx * c.slitWidth * c.slitWidth * this.head.oral * this.head.oral / (An * An * An) : 0;
        const U = solveU(D, Zl + Zr + Rv, (D >= 0) === (Ar > Al) ? a : 0);
        nL[i] = R[i] - Zl * U; nR[i + 1] = L[i + 1] + Zr * U;
        const wk = this.wallAt.indexOf(i);
        if (wk >= 0) {   // a yielding-wall branch: the joint's pressure drives a mass with friction and a spring, and what the wall takes is
          // missing from the joint (its pressure falls by Uwall / (Y1 + Y2)). Faded out as the place narrows -- a constriction's
          // joint belongs to the jet -- and FADED, not switched: a branch that cuts in and out carries its flow with it, as a click
          const gw = An <= .15 ? 0 : An >= .45 ? 1 : (An - .15) / .3, W = c.walls, Sk = this.wallS / this.wallAt.length;
          if (gw > 0) { const dp = gw * this.wallU[wk] / (Al / rc + Ar / rc); nL[i] -= dp; nR[i + 1] -= dp; }
          const pj = R[i] + nL[i];
          const th = this.head.mean;      // (a smaller head's walls are thinner: mass, friction and spring per cm2 go with the thickness)
          this.wallU[wk] += (gw * pj - W.resistance * th / Sk * this.wallU[wk] - W.stiffness * th / Sk * this.wallX[wk]) * Sk / (W.mass * th) / (2 * this.fs);
          this.wallX[wk] += this.wallU[wk] / (2 * this.fs);
        }
      }
      // ---- the velum: mouth-behind, mouth-ahead and nose meet at one pressure
      if (this.velum > 1e-4) {
        const i = this.velumAt, Y1 = Math.max(A[i], minA) / rc, Y2 = Math.max(A[i + 1], minA) / rc, Y3 = this.velum / rc;
        const p = 2 * (Y1 * R[i] + Y2 * L[i + 1] + Y3 * this.nLl[0]) / (Y1 + Y2 + Y3);
        nL[i] = p - R[i]; nR[i + 1] = p - L[i + 1]; this.nnR[0] = p - this.nLl[0]; this.noseLive = this.fs;
      } else if (this.noseLive > 0) this.nnR[0] = this.nLl[0];           // port shut: the nose rings on by itself, then is skipped
      // ---- the piriform sinuses: a closed side branch, as a delay there and back
      if (this.pirA > 0) { const i = this.pirAt; this.pp = (this.pp + 1) & 63;
        const D = this.pirD, k = Math.floor(D), f = D - k, back = this.pb[(this.pp - k) & 63] * (1 - f) + this.pb[(this.pp - k - 1) & 63] * f;
        if (A[i] >= .3 && A[i + 1] >= .3) { const Y1 = A[i] / rc, Y2 = A[i + 1] / rc, Y3 = this.pirA / rc, p = 2 * (Y1 * R[i] + Y2 * L[i + 1] + Y3 * back) / (Y1 + Y2 + Y3);
          nL[i] = p - R[i]; nR[i + 1] = p - L[i + 1]; this.pb[this.pp] = (p - back) * c.piriform.reflect; }
        else this.pb[this.pp] = back * c.piriform.reflect; }
      // ---- turbulence: where the pipe is narrowest the air is a jet, and past a critical speed the jet is noise.
      // The narrowest section is found directly (the lips included -- f is made there), the flow through it read from
      // its own two waves, and the noise put in where the jet ends: the first section downstream that is clearly
      // wider, or the open air if the jet IS the lips.
      {
        let m = -1, mA = nz.maxArea; for (let i = 1; i < N; i++) if (A[i] < mA && A[i] >= minA) { mA = A[i]; m = i; }
        this.meter.noise = 0;
        if (m >= 0) {
          const U = Math.abs(nR[m] - nL[m]) * mA / rc, Re = AIR.rho * U * Math.sqrt(4 / (Math.PI * mA)) / AIR.mu, over = Re * Re - nz.reCrit * nz.reCrit;
          this.Uc = U;
          this.overNow = (this.overNow ?? 0) + (Math.max(0, over) - (this.overNow ?? 0)) * nz.buildUp;   // turbulence takes a few ms to develop: a release is not noisy in its first instant
          if (over > 0) {
            const w = this.rnd(), keepN = Math.exp(-2 * Math.PI * nz.lowHz / (2 * this.fs)); this.noiseLP = keepN * this.noiseLP + (1 - keepN) * w;
            const toTeeth = (this.teethAt - m) * this.dx, hits = toTeeth < nz.teethReach[0] || toTeeth > nz.teethReach[1] ? 0 : Math.min(1, (nz.teethReach[1] - toTeeth) / Math.max(.1, nz.teethReach[1] - nz.teethFull));   // (a jet that has further to go strikes the teeth with less: sh is not louder than s)
            const keepH = Math.exp(-2 * Math.PI * nz.highHz / (2 * this.fs)); this.noiseHP = keepH * this.noiseHP + (1 - keepH) * (w - this.noiseLP); this.noiseH2 = keepH * (this.noiseH2 ?? 0) + (1 - keepH) * this.noiseHP;
            const ov = Math.min(over, this.overNow), lvl = ov <= nz.knee ? ov : Math.sqrt(ov * nz.knee);   // past the knee the noise grows with the flow, not its square: a release's surge of air is a burst, not an explosion
            const amp = this.noiseH2 * 3.4 * lvl * nz.gain * (nz.wall + (1 - nz.wall) * hits);        // (white, less its low end and its top: a jet's noise is a broad hump, not a hiss to 20kHz)
            let d = m + 1; while (d < N && A[d] < 1.5 * mA) d++;
            if (d < N) { for (let k = 0; k < nz.spread && d + k < N; k++) nR[d + k] += amp / nz.spread; } else lipNoise = amp;
            this.meter.noise = Math.abs(amp);
          }
        }
      }
      // ---- the lips: a fractional delay for the length that is not a whole section, then the open end
      {
        const Al = Math.max(A[N - 1], minA), dl = this.dl, dr = this.dr, n = 32;
        dl[this.dp] = R[N - 1];
        const e = this.lipExtra, k = Math.floor(e), f = e - k, at = (j) => (this.dp - j + 2 * n) % n;
        const arrive = dl[at(k)] * (1 - f) + dl[at(k + 1)] * f;          // the outgoing wave, `e` half-samples later
        let back = 0, flow = 0;
        if (A[N - 1] >= minA) {
          const r = Math.sqrt(Al / Math.PI), a1 = Math.exp(-2 * Math.PI * c.lips.cornerK * AIR.c / (2 * Math.PI * r) / (2 * this.fs));
          this.lipLP = a1 * this.lipLP + (1 - a1) * arrive; back = -c.lips.reflect * this.lipLP; flow = (arrive - back) * Al / rc + lipNoise * c.noise.lipGain;
        } else back = arrive;
        dr[this.dp] = back; nL[N - 1] = dr[at(k)] * (1 - f) + dr[at(k + 1)] * f;
        out += flow;
      }
      // ---- the two rooms that open and shut with the tongue: under a raised blade, and behind a lateral's closure
      if (this.sublA > 1e-4) { this.slp = (this.slp + 1) & 63; this.room(this.sublAt, this.sublA, this.sublD, this.slb, this.slp, c.sublingual.reflect, R, L, nR, nL, minA); }
      if (this.latA > 1e-4) { this.lpp = (this.lpp + 1) & 63; this.room(this.latAt, this.latA, this.latD, this.lfw, this.lpp, c.lateralPocket.reflect, R, L, nR, nL, minA); }
      // ---- the road round a lateral: the air leaves the midline behind the closure, goes by the tongue's sides and comes back in
      // front of it. Two three-way joints and a pipe between them -- and what is left of the midline behind the closure is a DEAD END,
      // which is where an /l/'s zero comes from. (As a leak through the closure, which is what it was, there is no dead end and no zero.)
      // ---- the nose
      if (this.noseLive > 0) {
        const M = this.M, a = this.nA, r = this.nRr, l = this.nLl, nr = this.nnR, nl = this.nnL;
        { const a1 = Math.max(this.velum, 1e-4), a0 = a[0]; if (a1 !== a0) { const k = a0 / a1, pp = r[0] + l[0], dd = (r[0] - l[0]) * k; r[0] = (pp + dd) / 2; l[0] = (pp - dd) / 2; a[0] = a1; } }   // (its pressure and flow kept as it changes size, like every other section)
        //      // THE PORT IS THE NOSE'S FIRST SECTION: what the three-way joint admits must be what travels on. With the
                                                // nose's full area there, a nearly shut port passed the mouth's whole pressure into a wide pipe -- energy from nowhere
        for (let i = 0; i + 1 < M; i++) { const Zl = 1 / a[i], Zr = 1 / a[i + 1], U = 2 * (r[i] - l[i + 1]) / (Zl + Zr); nl[i] = r[i] - Zl * U; nr[i + 1] = l[i + 1] + Zr * U; }   // (plain joints: the nose has no jets worth the square root; rho c cancels)
        // ---- the sinuses: what each room takes is missing from its joint (its pressure falls by U / (Y1 + Y2)), and the air in the
        // ostium is a mass on the room's spring: M dU/dt = p - X/C - R U. The same shape as a yielding wall, with a sharper tuning.
        for (const S of this.sin) { const i = S.at, Y1 = a[i] / rc, Y2 = a[i + 1] / rc, dp = S.U / (Y1 + Y2);
          nl[i] -= dp; nr[i + 1] -= dp;
          const pj = r[i] + nl[i];
          S.U += (pj - S.X / S.C - S.R * S.U) / S.M / (2 * this.fs);
          S.X += S.U / (2 * this.fs); }
        const An = c.nostril.area * this.head.area, rr = Math.sqrt(An / Math.PI), a1 = Math.exp(-2 * Math.PI * c.nostril.cornerK * AIR.c / (2 * Math.PI * rr) / (2 * this.fs));
        this.nosLP = a1 * this.nosLP + (1 - a1) * r[M - 1]; nl[M - 1] = -c.nostril.reflect * this.nosLP;
        out += (r[M - 1] - nl[M - 1]) * a[M - 1] / rc;
        if (this.velum <= 1e-4) this.noseLive--;
        for (let i = 0; i < M; i++) { const e = c.wallLoss * 2.2 * .5 * (nr[i] - nl[i]); r[i] = nr[i] - e; l[i] = nl[i] + e; }
      }
      // ---- travel one section, losing a little to the walls
      const kc = 1 - Math.exp(-2 * Math.PI * (c.wallLossCornerHz ?? 3000) / (2 * this.fs)), hiLoss = c.wallLossHigh ?? 0, dLP = this.dLP;
      for (let i = 0; i < N; i++) { const d = .5 * (nR[i] - nL[i]), q = 1 / Math.sqrt(Math.max(A[i], .05)); dLP[i] += kc * (d - dLP[i]); const e = q * (c.wallLoss * d + hiLoss * (d - dLP[i])); R[i] = nR[i] - e; L[i] = nL[i] + e; }
    }
    this.meter.Ug = this.U0; this.meter.Pm = this.R[this.velumAt] + this.L[this.velumAt];
    let uw = 0; for (let k = 0; k < this.wallU.length; k++) uw += this.wallU[k];
    this.uwSlow = (this.uwSlow ?? 0) + (uw - (this.uwSlow ?? 0)) * (2 * Math.PI * c.walls.radiateAboveHz / this.fs); uw -= this.uwSlow;   // (only what moves at the voice's pace: the slow swell of the cheeks as pressure builds is not a sound)
    const u = out * .5 + uw * c.walls.radiate, y0 = (u - this.uPrev) * c.radiation; this.uPrev = u;    // what is heard is the flow's rate of change
    // (a wave caught between two neighbouring joints goes round once per sample: energy at exactly the top of the band,
    // which is the model's grain and not a sound. The mean of two successive samples has a zero precisely there.)
    const y = (y0 + (this.yPrev ?? 0)) * .5; this.yPrev = y0;
    if (!(y > -1e9 && y < 1e9)) { this.meter.blewUp = (this.meter.blewUp ?? 0) + 1; this.meter.where = `U0 ${this.U0} Uc ${this.Uc} minA ${Math.min(...this.A).toExponential(2)} wallU ${[...this.wallU].map((v) => v.toExponential(1))} lipLP ${this.lipLP}`; this.reset(); return 0; }   // never hand NaN to a loudspeaker
    return y;
  }
}
