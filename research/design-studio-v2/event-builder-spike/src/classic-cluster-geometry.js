import { createRoundLatexBalloonVisual } from "./balloon-visual-model.js";

const round = (value, places = 4) => Number(value.toFixed(places));

const roundVector = (vector, places = 4) => vector.map((value) => round(value, places));

const degToRad = (degrees) => (degrees * Math.PI) / 180;

const normalize = (vector) => {
  const length = Math.hypot(...vector);
  return length === 0 ? [0, 0, 0] : vector.map((value) => value / length);
};

const addVectors = (a, b) => a.map((value, index) => value + b[index]);

const slotOffset = (radiusFt, degrees) => {
  const radians = degToRad(degrees);
  return [Math.cos(radians) * radiusFt, 0, Math.sin(radians) * radiusFt];
};

const repeatedColor = (colors, index) => colors[index % colors.length] || "Red";

const contactTo = (fromPosition, toBalloon) => {
  const normal = normalize([
    toBalloon.local_position[0] - fromPosition[0],
    toBalloon.local_position[1] - fromPosition[1],
    toBalloon.local_position[2] - fromPosition[2],
  ]);

  return {
    withBalloonId: toBalloon.balloon_id,
    pressure: 0.28,
    normal: roundVector(normal),
  };
};

function createClusterBalloon({
  balloonId,
  colorName,
  finish = "standard",
  sizedDiameterIn,
  localPosition,
  contacts = [],
  centerPressure = 0,
  slot,
  knotAxis = [0, -1, 0],
}) {
  const balloon = createRoundLatexBalloonVisual({
    balloonId,
    colorName,
    finish,
    sizedDiameterIn,
    inflationProfile: "properly_sized_cluster",
    contacts,
    centerPressure,
    nozzleAxis: knotAxis,
  });

  return {
    ...balloon,
    slot,
    local_position: roundVector(localPosition),
    knot_axis: knotAxis,
    tie_point: roundVector([0, -balloon.dimensions.radius_ft * 0.42, 0]),
  };
}

export function createDupletVisual(options = {}) {
  const clusterId = options.clusterId || "duplet";
  const colors = options.colors || ["Red", "White"];
  const sizedDiameterIn = options.sizedDiameterIn ?? 10;
  const diameterFt = sizedDiameterIn / 12;
  const separationFt = diameterFt * 0.62;
  const localPositions = [
    [-separationFt / 2, 0, 0],
    [separationFt / 2, 0, 0],
  ];
  const ids = [`${clusterId}-a`, `${clusterId}-b`];
  const contactPressure = 0.34;
  const balloonShells = ids.map((balloonId, index) => ({
    balloon_id: balloonId,
    local_position: roundVector(localPositions[index]),
  }));

  const balloons = balloonShells.map((shell, index) => {
    const other = balloonShells[index === 0 ? 1 : 0];
    const normal = normalize([
      other.local_position[0] - shell.local_position[0],
      other.local_position[1] - shell.local_position[1],
      other.local_position[2] - shell.local_position[2],
    ]);

    return createClusterBalloon({
      balloonId: shell.balloon_id,
      colorName: repeatedColor(colors, index),
      finish: options.finish || "standard",
      sizedDiameterIn,
      localPosition: shell.local_position,
      centerPressure: contactPressure,
      slot: index + 1,
      contacts: [
        {
          withBalloonId: other.balloon_id,
          pressure: contactPressure,
          normal: roundVector(normal),
        },
      ],
    });
  });

  return {
    construction_unit: "duplet",
    cluster_id: clusterId,
    sized_diameter_in: sizedDiameterIn,
    diameter_ft: round(diameterFt),
    tie_pressure: contactPressure,
    balloons,
  };
}

export function createQuadClusterVisual(options = {}) {
  const clusterId = options.clusterId || "quad";
  const colors = options.colors || ["Red", "White"];
  const sizedDiameterIn = options.sizedDiameterIn ?? 10;
  const diameterFt = sizedDiameterIn / 12;
  const clusterCenter = options.center || [0, 0, 0];
  const clusterRotationDeg = options.clusterRotationDeg ?? 0;
  const radiusFt = diameterFt * 0.43;
  const centerPressure = options.centerPressure ?? 0.58;
  const baseAngles = [0, 90, 180, 270];
  const shells = baseAngles.map((angle, index) => {
    const localOffset = slotOffset(radiusFt, angle + clusterRotationDeg);
    const localPosition = addVectors(clusterCenter, localOffset);

    return {
      balloon_id: `${clusterId}-slot-${index + 1}`,
      slot: index + 1,
      colorName: repeatedColor(colors, index),
      local_position: roundVector(localPosition),
    };
  });

  const balloons = shells.map((shell) => {
    const contacts = shells
      .filter((candidate) => candidate.balloon_id !== shell.balloon_id)
      .map((candidate) => contactTo(shell.local_position, candidate));

    return createClusterBalloon({
      balloonId: shell.balloon_id,
      colorName: shell.colorName,
      finish: options.finish || "standard",
      sizedDiameterIn,
      localPosition: shell.local_position,
      contacts,
      centerPressure,
      slot: shell.slot,
    });
  });

  return {
    construction_unit: "quad",
    cluster_id: clusterId,
    cluster_center: roundVector(clusterCenter),
    cluster_rotation_deg: clusterRotationDeg,
    sized_diameter_in: sizedDiameterIn,
    diameter_ft: round(diameterFt),
    center_pressure: round(centerPressure),
    adjacent_cluster_ids: [],
    balloons,
  };
}

export function createNestedQuadClusters(options = {}) {
  const pieceId = options.pieceId || "nested-quad-chain";
  const count = Math.max(1, options.count ?? 2);
  const colors = options.colors || ["Red", "White"];
  const sizedDiameterIn = options.sizedDiameterIn ?? 10;
  const rotationStepDeg = options.rotationStepDeg ?? 45;
  const diameterFt = sizedDiameterIn / 12;
  const verticalSpacingFt = diameterFt * 0.78;

  const clusters = Array.from({ length: count }, (_, index) =>
    createQuadClusterVisual({
      clusterId: `${pieceId}-cluster-${index + 1}`,
      colors,
      sizedDiameterIn,
      finish: options.finish || "standard",
      clusterRotationDeg: index * rotationStepDeg,
      center: [0, index * verticalSpacingFt, 0],
      centerPressure: options.centerPressure ?? 0.58,
    }),
  );

  clusters.forEach((cluster, index) => {
    cluster.adjacent_cluster_ids = [
      clusters[index - 1]?.cluster_id,
      clusters[index + 1]?.cluster_id,
    ].filter(Boolean);
  });

  return {
    construction_unit: "nested_quad_chain",
    piece_id: pieceId,
    sized_diameter_in: sizedDiameterIn,
    rotation_step_deg: rotationStepDeg,
    clusters,
    balloons: clusters.flatMap((cluster) => cluster.balloons),
  };
}
