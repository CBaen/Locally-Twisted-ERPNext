export const EVENT_PLAYGROUND_CONSTRUCTION_VERSION = "event-playground-construction-0.1.0";

const degToRad = (degrees) => (degrees * Math.PI) / 180;

const round = (value, places = 4) => Number(value.toFixed(places));

const roundVector = (vector, places = 4) => ({
  x: round(vector.x, places),
  y: round(vector.y, places),
  z: round(vector.z, places)
});

const normalize = (vector) => {
  const length = Math.hypot(vector.x, vector.y, vector.z);
  if (length < 0.0001) return { x: 0, y: -1, z: 0 };
  return {
    x: vector.x / length,
    y: vector.y / length,
    z: vector.z / length
  };
};

export function createClassicQuadRenderSlots(options = {}) {
  const radius = options.radius ?? 0.31;
  const zOffset = options.zOffset ?? 0.08;
  const phase = degToRad(options.phaseDeg ?? 0);
  const tieCenter = options.tieCenter || { x: 0, y: 0, z: 0 };

  return [0, Math.PI / 2, Math.PI, Math.PI * 1.5].map((angle, index) => {
    const localPosition = {
      x: Math.cos(angle + phase) * radius,
      y: Math.sin(angle + phase) * radius,
      z: index % 2 ? zOffset : -zOffset
    };
    const neckDirection = normalize({
      x: tieCenter.x - localPosition.x,
      y: tieCenter.y - localPosition.y,
      z: tieCenter.z - localPosition.z
    });

    return {
      construction_unit: "classic_quad_slot",
      slot: index + 1,
      local_position: roundVector(localPosition),
      tie_center: roundVector(tieCenter),
      neck_direction: roundVector(neckDirection),
      orientation_basis: "neck_and_knot_point_to_shared_quad_tie_center"
    };
  });
}
