const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));

const round = (value, places = 4) => Number(value.toFixed(places));

const roundVector = (vector, places = 4) => vector.map((value) => round(value, places));

export const BALLOON_VISUAL_VERSION = "balloon-visual-model-0.1.0";

export const BALLOON_SIZE_PROFILES = {
  round_latex_11_standard: {
    primitive_family: "round_latex",
    nominal_size_in: 11,
    listed_inflated_diameter_in: 11,
    listed_gas_capacity_cuft: 0.5,
    listed_gas_capacity_m3: 0.015,
    default_sized_diameter_in: 10,
    sizing_basis: "lab_default_pending_lt_approval",
    profile_note:
      "Default render size is intentionally conservative until LT approves exact packed cluster sizing.",
  },
};

export const COLOR_SWATCHES = {
  Red: "#d92f2f",
  White: "#f6f0e8",
  Blue: "#2468c9",
  Yellow: "#f4c542",
  Green: "#2f9d65",
  Black: "#1b1716",
  Gold: "#cda349",
  "Pearl Ivory": "#f4e4c8",
  "Reflex Gold": "#d4a93f",
  "Jewel Magenta": "#bd2e72",
};

const FINISH_PRESETS = {
  standard: {
    roughness: 0.48,
    specular_intensity: 0.46,
    clearcoat: 0.18,
    sheen: 0.58,
    opacity: 1,
  },
  reflex: {
    roughness: 0.24,
    specular_intensity: 0.9,
    clearcoat: 0.68,
    sheen: 0.74,
    opacity: 1,
  },
  pearl: {
    roughness: 0.34,
    specular_intensity: 0.72,
    clearcoat: 0.46,
    sheen: 0.86,
    opacity: 1,
  },
  jewel: {
    roughness: 0.28,
    specular_intensity: 0.78,
    clearcoat: 0.54,
    sheen: 0.62,
    opacity: 0.88,
  },
};

const INFLATION_PRESETS = {
  underinflated: {
    body_scale: [0.86, 0.93, 0.86],
    neck_scale: [0.1, 0.12, 0.1],
    knot_scale: [0.13, 0.08, 0.13],
    neck_inflation: 0.08,
    radial_pressure: 0.38,
    axial_tension: 0.32,
    contact_response: 0.54,
    profile_note: "Soft, visibly smaller, and less contact-stable.",
  },
  proper_teardrop: {
    body_scale: [0.98, 1.08, 0.98],
    neck_scale: [0.15, 0.24, 0.15],
    knot_scale: [0.18, 0.1, 0.18],
    neck_inflation: 0.26,
    radial_pressure: 0.62,
    axial_tension: 0.54,
    contact_response: 0.76,
    profile_note: "Properly inflated round latex reads as a round teardrop with neck and knot.",
  },
  properly_sized_cluster: {
    body_scale: [0.96, 1.05, 0.96],
    neck_scale: [0.14, 0.22, 0.14],
    knot_scale: [0.18, 0.1, 0.18],
    neck_inflation: 0.24,
    radial_pressure: 0.66,
    axial_tension: 0.58,
    contact_response: 0.82,
    profile_note: "Sized for repeated classic clusters where neighboring balloons share contact load.",
  },
  overinflated: {
    body_scale: [1.06, 1.14, 1.06],
    neck_scale: [0.22, 0.38, 0.22],
    knot_scale: [0.19, 0.11, 0.19],
    neck_inflation: 0.78,
    radial_pressure: 0.9,
    axial_tension: 0.86,
    contact_response: 0.94,
    profile_note: "Tight latex with more neck inflation and stronger contact highlights.",
  },
};

const resolveColor = (colorName, colorHex) => colorHex || COLOR_SWATCHES[colorName] || colorName || "#d92f2f";

const normalizeFinish = (finish = "standard") =>
  Object.hasOwn(FINISH_PRESETS, finish) ? finish : "standard";

const normalizeInflationProfile = (profile = "proper_teardrop") =>
  Object.hasOwn(INFLATION_PRESETS, profile) ? profile : "proper_teardrop";

const normalizeContact = (contact) => ({
  withBalloonId: contact.withBalloonId,
  pressure: round(clamp(contact.pressure ?? 0.18)),
  normal: roundVector(contact.normal || [0, 0, 1]),
});

export function createFinishMaterial(finish = "standard", colorHex = "#d92f2f") {
  const finishName = normalizeFinish(finish);
  const preset = FINISH_PRESETS[finishName];

  return {
    finish: finishName,
    color_hex: colorHex,
    diffuse_hex: colorHex,
    metalness: 0,
    roughness: preset.roughness,
    specular_intensity: preset.specular_intensity,
    clearcoat: preset.clearcoat,
    sheen: preset.sheen,
    opacity: preset.opacity,
    material_note: "Latex finish response only; metalness stays zero for all balloon latex.",
  };
}

export function createRoundLatexBalloonVisual(options = {}) {
  const profile = BALLOON_SIZE_PROFILES.round_latex_11_standard;
  const nominalSizeIn = options.nominalSizeIn ?? profile.nominal_size_in;
  const sizedDiameterIn = options.sizedDiameterIn ?? profile.default_sized_diameter_in;
  const sizingBasis = options.sizedDiameterIn ? "explicit" : profile.sizing_basis;
  const diameterFt = sizedDiameterIn / 12;
  const inflationProfile = normalizeInflationProfile(options.inflationProfile);
  const inflation = INFLATION_PRESETS[inflationProfile];
  const colorName = options.colorName || "Red";
  const colorHex = resolveColor(colorName, options.colorHex);
  const contacts = (options.contacts || []).map(normalizeContact);
  const contactPressure =
    contacts.length === 0
      ? 0
      : contacts.reduce((total, contact) => total + contact.pressure, 0) / contacts.length;
  const centerPressure = clamp(options.centerPressure ?? 0);

  return {
    visual_version: BALLOON_VISUAL_VERSION,
    balloon_id: options.balloonId || "balloon-visual",
    primitive_family: profile.primitive_family,
    nominal_size_in: nominalSizeIn,
    listed_inflated_diameter_in: profile.listed_inflated_diameter_in,
    sized_diameter_in: sizedDiameterIn,
    sizing_basis: sizingBasis,
    dimensions: {
      diameter_in: sizedDiameterIn,
      diameter_ft: round(diameterFt),
      radius_ft: round(diameterFt / 2),
    },
    color: {
      name: colorName,
      hex: colorHex,
    },
    material: createFinishMaterial(options.finish || "standard", colorHex),
    inflation: {
      profile: inflationProfile,
      neck_inflation: inflation.neck_inflation,
      note: inflation.profile_note,
    },
    shape: {
      body_scale: [...inflation.body_scale],
      neck_scale: [...inflation.neck_scale],
      knot_scale: [...inflation.knot_scale],
      body_origin: [0, 0, 0],
      neck_origin: roundVector([0, -0.52 * diameterFt, 0]),
      knot_origin: roundVector([0, -0.66 * diameterFt, 0]),
      contact_flattening: round(clamp(contactPressure * 0.12 + centerPressure * 0.08)),
    },
    orientation: {
      nozzle_axis: options.nozzleAxis || [0, -1, 0],
      display_axis: "y",
    },
    contacts,
    tension: {
      radial_pressure: round(clamp(inflation.radial_pressure + contactPressure * 0.08 + centerPressure * 0.04)),
      axial_tension: round(clamp(inflation.axial_tension + centerPressure * 0.06)),
      contact_pressure: round(contactPressure),
      center_pressure: round(centerPressure),
      contact_response: inflation.contact_response,
      contacts,
    },
  };
}

export function createInflationSamples(options = {}) {
  return ["underinflated", "proper_teardrop", "overinflated"].map((inflationProfile) =>
    createRoundLatexBalloonVisual({
      ...options,
      balloonId: `${options.balloonId || "inflation-sample"}-${inflationProfile}`,
      inflationProfile,
    }),
  );
}

export function listFinishSamples(options = {}) {
  return [
    ["standard", options.standardColor || "Red"],
    ["reflex", options.reflexColor || "Reflex Gold"],
    ["pearl", options.pearlColor || "Pearl Ivory"],
    ["jewel", options.jewelColor || "Jewel Magenta"],
  ].map(([finish, colorName]) =>
    createRoundLatexBalloonVisual({
      ...options,
      balloonId: `${options.balloonId || "finish-sample"}-${finish}`,
      colorName,
      finish,
      inflationProfile: options.inflationProfile || "proper_teardrop",
    }),
  );
}
