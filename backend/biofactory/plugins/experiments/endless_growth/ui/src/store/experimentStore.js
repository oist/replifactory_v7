export default {
  namespaced: true,
  state: {
    experiments: {
      c435ed55: {
        alive: true,
        class: "biofactory.experiment.ODMeasureExperiment",
        cycleTime: 5,
        cycles: 1,
        endTime: null,
        id: "c435ed55",
        interrupted: false,
        name: "Optical Density Measure",
        startTime: "Tue, 16 Jul 2024 06:29:13 GMT",
        status: "runing",
      },
      d82a117c: {
        alive: true,
        class: "biofactory.experiment.EndlessGrowthExperiment",
        cycleTime: 60,
        cycles: 2,
        endTime: null,
        id: "d82a117c",
        interrupted: false,
        name: "Endless Growth",
        startTime: "Tue, 16 Jul 2024 06:27:53 GMT",
        status: "runing",
        dataset: [],
        events: [],
      },
    },
  },
  getters: {
    getExperiment: (state) => (id) => {
      return state.experiments[id];
    },
  },
  mutations: {
    updateExperiment(state, { id, data }) {
      state.experiments[id] = data;
    },
    updateExperimentsStatuses(state, data) {
      state.experiments = data;
    },
  },
  actions: {
    fetchExperiment({ commit }, id) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const data = {
            alive: true,
            class: "biofactory.experiment.EndlessGrowthExperiment",
            cycleTime: 60,
            cycles: 2,
            endTime: null,
            id: "d82a117c",
            interrupted: false,
            name: "Endless Growth",
            startTime: "2024-07-12 07:43:58",
            status: "runing",
            events: [
              {
                datetime: "2024-07-12 07:43:58",
                name: "Start",
              },
              {
                datetime: "2024-12-14 07:43:58",
                name: "System Reboot",
              },
              {
                datetime: "2025-02-14 07:43:58",
                name: "End",
              },
            ],
            dataset: [
              {
                meta: {
                  name: "OD Reactor 1",
                },
                source: [
                  ["cycle", "datetime", "optical_density"],
                  [1, "2024-07-12 07:43:58", 0.361],
                  [2, "2024-07-13 07:43:58", 0.337],
                  [3, "2024-07-14 07:43:58", 0.319],
                  [4, "2024-07-15 07:43:58", 0.309],
                  [5, "2024-07-16 07:43:58", 0.309],
                  [6, "2024-07-17 07:43:58", 0.309],
                  [7, "2024-07-18 07:43:58", 0.309],
                  [8, "2024-07-19 07:43:58", 0.309],
                  [9, "2024-07-20 07:43:58", 0.309],
                  [10, "2024-07-21 07:43:58", 0.309],
                  [11, "2024-07-22 07:43:58", 0.31],
                  [12, "2024-07-23 07:43:58", 0.31],
                  [13, "2024-07-24 07:43:58", 0.31],
                  [14, "2024-07-25 07:43:58", 0.31],
                  [15, "2024-07-26 07:43:58", 0.311],
                  [16, "2024-07-27 07:43:58", 0.312],
                  [17, "2024-07-28 07:43:58", 0.312],
                  [18, "2024-07-29 07:43:58", 0.313],
                  [19, "2024-07-30 07:43:58", 0.313],
                  [20, "2024-07-31 07:43:58", 0.314],
                  [21, "2024-08-01 07:43:58", 0.316],
                  [22, "2024-08-02 07:43:58", 0.316],
                  [23, "2024-08-03 07:43:58", 0.318],
                  [24, "2024-08-04 07:43:58", 0.32],
                  [25, "2024-08-05 07:43:58", 0.322],
                  [26, "2024-08-06 07:43:58", 0.325],
                  [27, "2024-08-07 07:43:58", 0.328],
                  [28, "2024-08-08 07:43:58", 0.332],
                  [29, "2024-08-09 07:43:58", 0.336],
                  [30, "2024-08-10 07:43:58", 0.341],
                  [31, "2024-08-11 07:43:58", 0.348],
                  [32, "2024-08-12 07:43:58", 0.356],
                  [33, "2024-08-13 07:43:58", 0.364],
                  [34, "2024-08-14 07:43:58", 0.374],
                  [35, "2024-08-15 07:43:58", 0.388],
                  [36, "2024-08-16 07:43:58", 0.403],
                  [37, "2024-08-17 07:43:58", 0.42],
                  [38, "2024-08-18 07:43:58", 0.442],
                  [39, "2024-08-19 07:43:58", 0.461],
                  [40, "2024-08-20 07:43:58", 0.485],
                  [41, "2024-08-21 07:43:58", 0.516],
                  [42, "2024-08-22 07:43:58", 0.553],
                  [43, "2024-08-23 07:43:58", 0.596],
                  [44, "2024-08-24 07:43:58", 0.643],
                  [45, "2024-08-25 07:43:58", 0.678],
                  [46, "2024-08-26 07:43:58", 0.712],
                  [47, "2024-08-27 07:43:58", 0.73],
                  [48, "2024-08-28 07:43:58", 0.73],
                  [49, "2024-08-29 07:43:58", 0.731],
                  [50, "2024-08-30 07:43:58", 0.742],
                  [51, "2024-08-31 07:43:58", 0.742],
                  [52, "2024-09-01 07:43:58", 0.739],
                  [53, "2024-09-02 07:43:58", 0.738],
                  [54, "2024-09-03 07:43:58", 0.736],
                  [55, "2024-09-04 07:43:58", 0.74],
                  [56, "2024-09-05 07:43:58", 0.745],
                  [57, "2024-09-06 07:43:58", 0.746],
                  [58, "2024-09-07 07:43:58", 0.743],
                  [59, "2024-09-08 07:43:58", 0.74],
                  [60, "2024-09-09 07:43:58", 0.737],
                  [61, "2024-09-10 07:43:58", 0.733],
                  [62, "2024-09-11 07:43:58", 0.731],
                  [63, "2024-09-12 07:43:58", 0.728],
                  [64, "2024-09-13 07:43:58", 0.726],
                  [65, "2024-09-14 07:43:58", 0.722],
                  [66, "2024-09-15 07:43:58", 0.721],
                  [67, "2024-09-16 07:43:58", 0.718],
                  [68, "2024-09-17 07:43:58", 0.714],
                  [69, "2024-09-18 07:43:58", 0.712],
                  [70, "2024-09-19 07:43:58", 0.711],
                  [71, "2024-09-20 07:43:58", 0.707],
                  [72, "2024-09-21 07:43:58", 0.705],
                  [73, "2024-09-22 07:43:58", 0.702],
                  [74, "2024-09-23 07:43:58", 0.7],
                  [75, "2024-09-24 07:43:58", 0.699],
                  [76, "2024-09-25 07:43:58", 0.697],
                  [77, "2024-09-26 07:43:58", 0.694],
                  [78, "2024-09-27 07:43:58", 0.692],
                  [79, "2024-09-28 07:43:58", 0.689],
                  [80, "2024-09-29 07:43:58", 0.687],
                  [81, "2024-09-30 07:43:58", 0.685],
                  [82, "2024-10-01 07:43:58", 0.683],
                  [83, "2024-10-02 07:43:58", 0.68],
                  [84, "2024-10-03 07:43:58", 0.678],
                  [85, "2024-10-04 07:43:58", 0.676],
                  [86, "2024-10-05 07:43:58", 0.675],
                  [87, "2024-10-06 07:43:58", 0.671],
                  [88, "2024-10-07 07:43:58", 0.669],
                  [89, "2024-10-08 07:43:58", 0.668],
                  [90, "2024-10-09 07:43:58", 0.664],
                  [91, "2024-10-10 07:43:58", 0.661],
                  [92, "2024-10-11 07:43:58", 0.663],
                  [93, "2024-10-12 07:43:58", 0.661],
                  [94, "2024-10-13 07:43:58", 0.659],
                  [95, "2024-10-14 07:43:58", 0.657],
                  [96, "2024-10-15 07:43:58", 0.655],
                  [97, "2024-10-16 07:43:58", 0.654],
                  [98, "2024-10-17 07:43:58", 0.653],
                  [99, "2024-10-18 07:43:58", 0.651],
                  [100, "2024-10-19 07:43:58", 0.65],
                  [101, "2024-10-20 07:43:58", 0.649],
                  [102, "2024-10-21 07:43:58", 0.648],
                  [103, "2024-10-22 07:43:58", 0.646],
                  [104, "2024-10-23 07:43:58", 0.645],
                  [105, "2024-10-24 07:43:58", 0.644],
                  [106, "2024-10-25 07:43:58", 0.644],
                  [107, "2024-10-26 07:43:58", 0.643],
                  [108, "2024-10-27 07:43:58", 0.641],
                  [109, "2024-10-28 07:43:58", 0.641],
                  [110, "2024-10-29 07:43:58", 0.64],
                  [111, "2024-10-30 07:43:58", 0.638],
                  [112, "2024-10-31 07:43:58", 0.638],
                  [113, "2024-11-01 07:43:58", 0.637],
                  [114, "2024-11-02 07:43:58", 0.637],
                  [115, "2024-11-03 07:43:58", 0.635],
                  [116, "2024-11-04 07:43:58", 0.635],
                  [117, "2024-11-05 07:43:58", 0.634],
                  [118, "2024-11-06 07:43:58", 0.633],
                  [119, "2024-11-07 07:43:58", 0.632],
                  [120, "2024-11-08 07:43:58", 0.631],
                  [121, "2024-11-09 07:43:58", 0.63],
                  [122, "2024-11-10 07:43:58", 0.63],
                  [123, "2024-11-11 07:43:58", 0.629],
                  [124, "2024-11-12 07:43:58", 0.628],
                  [125, "2024-11-13 07:43:58", 0.628],
                  [126, "2024-11-14 07:43:58", 0.626],
                  [127, "2024-11-15 07:43:58", 0.626],
                  [128, "2024-11-16 07:43:58", 0.626],
                  [129, "2024-11-17 07:43:58", 0.625],
                  [130, "2024-11-18 07:43:58", 0.625],
                  [131, "2024-11-19 07:43:58", 0.624],
                  [132, "2024-11-20 07:43:58", 0.623],
                  [133, "2024-11-21 07:43:58", 0.623],
                  [134, "2024-11-22 07:43:58", 0.622],
                  [135, "2024-11-23 07:43:58", 0.622],
                  [136, "2024-11-24 07:43:58", 0.621],
                  [137, "2024-11-25 07:43:58", 0.62],
                  [138, "2024-11-26 07:43:58", 0.62],
                ],
              },
              {
                meta: {
                  name: "OD Reactor 3",
                },
                markedAreas: [
                  [
                    {
                      name: "Sampling",
                      xAxis: "2024-09-16 07:43:58",
                    },
                    {
                      xAxis: "2024-09-26 07:43:58",
                    },
                  ],
                  [
                    {
                      name: "Rest",
                      xAxis: "2024-11-26 07:43:58",
                    },
                    {
                      xAxis: "2024-11-30 07:43:58",
                    },
                  ],
                ],
                source: [
                  ["cycle", "datetime", "optical_density"],
                  [1, "2024-07-12 07:43:58", 0.385],
                  [2, "2024-07-13 07:43:58", 0.385],
                  [3, "2024-07-14 07:43:58", 0.385],
                  [4, "2024-07-15 07:43:58", 0.384],
                  [5, "2024-07-16 07:43:58", 0.384],
                  [6, "2024-07-17 07:43:58", 0.385],
                  [7, "2024-07-18 07:43:58", 0.385],
                  [8, "2024-07-19 07:43:58", 0.386],
                  [9, "2024-07-20 07:43:58", 0.386],
                  [10, "2024-07-21 07:43:58", 0.386],
                  [11, "2024-07-22 07:43:58", 0.386],
                  [12, "2024-07-23 07:43:58", 0.386],
                  [13, "2024-07-24 07:43:58", 0.387],
                  [14, "2024-07-25 07:43:58", 0.388],
                  [15, "2024-07-26 07:43:58", 0.388],
                  [16, "2024-07-27 07:43:58", 0.389],
                  [17, "2024-07-28 07:43:58", 0.389],
                  [18, "2024-07-29 07:43:58", 0.39],
                  [19, "2024-07-30 07:43:58", 0.39],
                  [20, "2024-07-31 07:43:58", 0.391],
                  [21, "2024-08-01 07:43:58", 0.393],
                  [22, "2024-08-02 07:43:58", 0.395],
                  [23, "2024-08-03 07:43:58", 0.396],
                  [24, "2024-08-04 07:43:58", 0.398],
                  [25, "2024-08-05 07:43:58", 0.401],
                  [26, "2024-08-06 07:43:58", 0.404],
                  [27, "2024-08-07 07:43:58", 0.407],
                  [28, "2024-08-08 07:43:58", 0.412],
                  [29, "2024-08-09 07:43:58", 0.418],
                  [30, "2024-08-10 07:43:58", 0.424],
                  [31, "2024-08-11 07:43:58", 0.431],
                  [32, "2024-08-12 07:43:58", 0.44],
                  [33, "2024-08-13 07:43:58", 0.45],
                  [34, "2024-08-14 07:43:58", 0.463],
                  [35, "2024-08-15 07:43:58", 0.478],
                  [36, "2024-08-16 07:43:58", 0.496],
                  [37, "2024-08-17 07:43:58", 0.517],
                  [38, "2024-08-18 07:43:58", 0.542],
                  [39, "2024-08-19 07:43:58", 0.565],
                  [40, "2024-08-20 07:43:58", 0.594],
                  [41, "2024-08-21 07:43:58", 0.629],
                  [42, "2024-08-22 07:43:58", 0.673],
                  [43, "2024-08-23 07:43:58", 0.72],
                  [44, "2024-08-24 07:43:58", 0.776],
                  [45, "2024-08-25 07:43:58", 0.812],
                  [46, "2024-08-26 07:43:58", 0.856],
                  [47, "2024-08-27 07:43:58", 0.878],
                  [48, "2024-08-28 07:43:58", 0.542],
                  [49, "2024-08-29 07:43:58", 0.565],
                  [50, "2024-08-30 07:43:58", 0.594],
                  [51, "2024-08-31 07:43:58", 0.629],
                  [52, "2024-09-01 07:43:58", 0.673],
                  [53, "2024-09-02 07:43:58", 0.72],
                  [54, "2024-09-03 07:43:58", 0.776],
                  [55, "2024-09-04 07:43:58", 0.812],
                  [56, "2024-09-05 07:43:58", 0.856],
                  [57, "2024-09-06 07:43:58", 0.878],
                  [58, "2024-09-07 07:43:58", 0.542],
                  [59, "2024-09-08 07:43:58", 0.565],
                  [60, "2024-09-09 07:43:58", 0.594],
                  [61, "2024-09-10 07:43:58", 0.629],
                  [62, "2024-09-11 07:43:58", 0.673],
                  [63, "2024-09-12 07:43:58", 0.72],
                  [64, "2024-09-13 07:43:58", 0.776],
                  [65, "2024-09-14 07:43:58", 0.812],
                  [66, "2024-09-15 07:43:58", 0.856],
                  [67, "2024-09-16 07:43:58", 0.878],
                  [68, "2024-09-17 07:43:58", null],
                  [69, "2024-09-18 07:43:58", null],
                  [70, "2024-09-19 07:43:58", null],
                  [71, "2024-09-20 07:43:58", null],
                  [72, "2024-09-21 07:43:58", null],
                  [73, "2024-09-22 07:43:58", null],
                  [74, "2024-09-23 07:43:58", null],
                  [75, "2024-09-24 07:43:58", null],
                  [76, "2024-09-25 07:43:58", null],
                  [77, "2024-09-26 07:43:58", 0.878],
                  [78, "2024-09-27 07:43:58", 0.542],
                  [79, "2024-09-28 07:43:58", 0.565],
                  [80, "2024-09-29 07:43:58", 0.594],
                  [81, "2024-09-30 07:43:58", 0.629],
                  [82, "2024-10-01 07:43:58", 0.673],
                  [83, "2024-10-02 07:43:58", 0.72],
                  [84, "2024-10-03 07:43:58", 0.776],
                  [85, "2024-10-04 07:43:58", 0.812],
                  [86, "2024-10-05 07:43:58", 0.856],
                  [87, "2024-10-06 07:43:58", 0.878],
                  [88, "2024-10-07 07:43:58", 0.542],
                  [89, "2024-10-08 07:43:58", 0.565],
                  [90, "2024-10-09 07:43:58", 0.594],
                  [91, "2024-10-10 07:43:58", 0.629],
                  [92, "2024-10-11 07:43:58", 0.673],
                  [93, "2024-10-12 07:43:58", 0.72],
                  [94, "2024-10-13 07:43:58", 0.776],
                  [95, "2024-10-14 07:43:58", 0.812],
                  [96, "2024-10-15 07:43:58", 0.856],
                  [97, "2024-10-16 07:43:58", 0.878],
                  [98, "2024-10-17 07:43:58", 0.542],
                  [99, "2024-10-18 07:43:58", 0.565],
                  [100, "2024-10-19 07:43:58", 0.594],
                  [101, "2024-10-20 07:43:58", 0.629],
                  [102, "2024-10-21 07:43:58", 0.673],
                  [103, "2024-10-22 07:43:58", 0.72],
                  [104, "2024-10-23 07:43:58", 0.776],
                  [105, "2024-10-24 07:43:58", 0.812],
                  [106, "2024-10-25 07:43:58", 0.856],
                  [107, "2024-10-26 07:43:58", 0.878],
                  [108, "2024-10-27 07:43:58", 0.542],
                  [109, "2024-10-28 07:43:58", 0.565],
                  [110, "2024-10-29 07:43:58", 0.594],
                  [111, "2024-10-30 07:43:58", 0.629],
                  [112, "2024-10-31 07:43:58", 0.673],
                  [113, "2024-11-01 07:43:58", 0.72],
                  [114, "2024-11-02 07:43:58", 0.776],
                  [115, "2024-11-03 07:43:58", 0.812],
                  [116, "2024-11-04 07:43:58", 0.856],
                  [117, "2024-11-05 07:43:58", 0.878],
                  [118, "2024-11-06 07:43:58", 0.542],
                  [119, "2024-11-07 07:43:58", 0.565],
                  [120, "2024-11-08 07:43:58", 0.594],
                  [121, "2024-11-09 07:43:58", 0.629],
                  [122, "2024-11-10 07:43:58", 0.673],
                  [123, "2024-11-11 07:43:58", 0.72],
                  [124, "2024-11-12 07:43:58", 0.776],
                  [125, "2024-11-13 07:43:58", 0.812],
                  [126, "2024-11-14 07:43:58", 0.856],
                  [127, "2024-11-15 07:43:58", 0.878],
                  [128, "2024-11-16 07:43:58", 0.883],
                  [129, "2024-11-17 07:43:58", 0.883],
                  [130, "2024-11-18 07:43:58", 0.9],
                  [131, "2024-11-19 07:43:58", 0.897],
                  [132, "2024-11-20 07:43:58", 0.889],
                  [133, "2024-11-21 07:43:58", 0.886],
                  [134, "2024-11-22 07:43:58", 0.885],
                  [135, "2024-11-23 07:43:58", 0.89],
                  [136, "2024-11-24 07:43:58", 0.896],
                  [137, "2024-11-25 07:43:58", 0.898],
                  [138, "2024-11-26 07:43:58", 0.897],
                  [139, "2024-11-27 07:43:58", 0.893],
                  [140, "2024-11-28 07:43:58", 0.889],
                  [141, "2024-11-29 07:43:58", 0.884],
                  [142, "2024-11-30 07:43:58", 0.882],
                  [143, "2024-12-01 07:43:58", 0.879],
                  [144, "2024-12-02 07:43:58", 0.875],
                  [145, "2024-12-03 07:43:58", 0.872],
                  [146, "2024-12-04 07:43:58", 0.87],
                  [147, "2024-12-05 07:43:58", 0.868],
                  [148, "2024-12-06 07:43:58", 0.864],
                  [149, "2024-12-07 07:43:58", 0.861],
                  [150, "2024-12-08 07:43:58", 0.859],
                  [151, "2024-12-09 07:43:58", 0.857],
                  [152, "2024-12-10 07:43:58", 0.855],
                  [153, "2024-12-11 07:43:58", 0.85],
                  [154, "2024-12-12 07:43:58", 0.849],
                  [155, "2024-12-13 07:43:58", 0.845],
                  [156, "2024-12-14 07:43:58", 0.844],
                  [157, "2024-12-15 07:43:58", 0.84],
                  [158, "2024-12-16 07:43:58", 0.838],
                  [159, "2024-12-17 07:43:58", 0.836],
                  [160, "2024-12-18 07:43:58", 0.834],
                  [161, "2024-12-19 07:43:58", 0.831],
                  [162, "2024-12-20 07:43:58", 0.829],
                  [163, "2024-12-21 07:43:58", 0.826],
                  [164, "2024-12-22 07:43:58", 0.824],
                  [165, "2024-12-23 07:43:58", 0.821],
                  [166, "2024-12-24 07:43:58", 0.819],
                  [167, "2024-12-25 07:43:58", 0.816],
                  [168, "2024-12-26 07:43:58", 0.815],
                  [169, "2024-12-27 07:43:58", 0.812],
                  [170, "2024-12-28 07:43:58", 0.81],
                  [171, "2024-12-29 07:43:58", 0.807],
                  [172, "2024-12-30 07:43:58", 0.806],
                  [173, "2024-12-31 07:43:58", 0.805],
                  [174, "2025-01-01 07:43:58", 0.805],
                  [175, "2025-01-02 07:43:58", 0.801],
                  [176, "2025-01-03 07:43:58", 0.8],
                  [177, "2025-01-04 07:43:58", 0.798],
                  [178, "2025-01-05 07:43:58", 0.797],
                  [179, "2025-01-06 07:43:58", 0.795],
                  [180, "2025-01-07 07:43:58", 0.793],
                  [181, "2025-01-08 07:43:58", 0.793],
                  [182, "2025-01-09 07:43:58", 0.79],
                  [183, "2025-01-10 07:43:58", 0.789],
                  [184, "2025-01-11 07:43:58", 0.787],
                  [185, "2025-01-12 07:43:58", 0.785],
                  [186, "2025-01-13 07:43:58", 0.784],
                  [187, "2025-01-14 07:43:58", 0.783],
                  [188, "2025-01-15 07:43:58", 0.781],
                  [189, "2025-01-16 07:43:58", 0.78],
                  [190, "2025-01-17 07:43:58", 0.778],
                  [191, "2025-01-18 07:43:58", 0.777],
                  [192, "2025-01-19 07:43:58", 0.776],
                  [193, "2025-01-20 07:43:58", 0.775],
                  [194, "2025-01-21 07:43:58", 0.774],
                  [195, "2025-01-22 07:43:58", 0.771],
                  [196, "2025-01-23 07:43:58", 0.771],
                  [197, "2025-01-24 07:43:58", 0.77],
                  [198, "2025-01-25 07:43:58", 0.769],
                  [199, "2025-01-26 07:43:58", 0.767],
                  [200, "2025-01-27 07:43:58", 0.767],
                  [201, "2025-01-28 07:43:58", 0.765],
                  [202, "2025-01-29 07:43:58", 0.764],
                  [203, "2025-01-30 07:43:58", 0.763],
                  [204, "2025-01-31 07:43:58", 0.761],
                  [205, "2025-02-01 07:43:58", 0.762],
                  [206, "2025-02-02 07:43:58", 0.761],
                  [207, "2025-02-03 07:43:58", 0.759],
                  [208, "2025-02-04 07:43:58", 0.759],
                  [209, "2025-02-05 07:43:58", 0.758],
                  [210, "2025-02-06 07:43:58", 0.757],
                  [211, "2025-02-07 07:43:58", 0.755],
                  [212, "2025-02-08 07:43:58", 0.755],
                  [213, "2025-02-09 07:43:58", 0.754],
                  [214, "2025-02-10 07:43:58", 0.753],
                  [215, "2025-02-11 07:43:58", 0.752],
                  [216, "2025-02-12 07:43:58", 0.751],
                  [217, "2025-02-13 07:43:58", 0.75],
                  [218, "2025-02-14 07:43:58", 0.75],
                ],
              },
            ],
          };
          commit("updateExperiment", { id: id, data: data });
          resolve(data);
        }, 1000);
      });
    },
  },
};
