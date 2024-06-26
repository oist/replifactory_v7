# Experiments

## Object model

```yml
# experiments/replifactory.experiment.MorbidostatExperiment/presets/slow_growth.yaml
experiment:
  class: replifactory.experiment.MorbidostatExperiment
  parameters:
    volume_added: 0.5  # ml
    od_threshold: 0.400
    od_threshold_first_dilution: 0.300
    stress_dose_first_dilution: 0.1  # ml
    stress_increase_delay_generations: 10
    stress_increase_tdoubling_max_hrs: 3
    stress_decrease_delay_hrs: 1
    stress_decrease_tdoubling_min_hrs: 0.5
  cultures:
    - culture_name: Escherichia coli
      culture_comment: MG1655

    - culture_name: Saccharomyces cerevisiae
      culture_comment: BY4741
      volume_fixed: 5.0  # ml
```

experiments/replifactory.experiment.MorbidostatExperiment/presets/slow_growth.yaml
experiments/replifactory.experiment.MorbidostatExperiment/runs/20240620_114735/_experiment.yaml

```yaml
experiment:
  class: replifactory.experiment.MorbidostatExperiment
  parameters:
    volume_added: 0.5  # ml
    od_threshold: 0.400
    od_threshold_first_dilution: 0.300
    stress_dose_first_dilution: 0.1  # ml
    stress_increase_delay_generations: 10
    stress_increase_tdoubling_max_hrs: 3
    stress_decrease_delay_hrs: 1
    stress_decrease_tdoubling_min_hrs: 0.5
  cultures:
    - culture_name: Escherichia coli
      culture_comment: MG1655
      reactor: reactor-1
    - culture_name: Saccharomyces cerevisiae
      culture_comment: BY4741
      reactor: reactor-2
machine:
    class: replifactory.machine.replifactory_v5.ReplifactoryMachine
    parameters:
      serial_number: FT05001
    reactors:
      reactor-1:
        volume_fixed: 5.0  # ml
      reactor-2:
        volume_fixed: 5.0  # ml
      reactor-3:
        volume_fixed: 5.0  # ml
      reactor-4:
        volume_fixed: 5.0  # ml
      reactor-5:
        volume_fixed: 5.0  # ml
      reactor-6:
        volume_fixed: 5.0  # ml
      reactor-7:
        volume_fixed: 5.0  # ml
    devices:
      pump-1:
        profile:
          acceleration: 0.0,
          deceleration: 0.0,
          max_speed_rps: 0,
          min_speed_rps: 0,
          full_step_speed: 0,
          kval_hold: 0,
          kval_run: 0,
          kval_acc: 0,
          kval_dec: 0,
          intersect_speed: 0,
          start_slope: 0,
          acceleration_final_slope: 0,
          deceleration_final_slope: 0,
          thermal_compensation_factor: 0,
          overcurrent_threshold: 0,
          stall_threshold: 0,
          step_mode: 0,
          alarm_enable: 0,
          clockwise: false,
      optical_density_sensor-1:
        mv_od_curve:
          0.300: 0.3
          0.400: 0.4
          0.500: 0.5
```

experiments/replifactory.experiment.MorbidostatExperiment/runs/20240620_114735/_experiment.log
experiments/replifactory.experiment.MorbidostatExperiment/runs/20240620_114735/reactor-1.csv
experiments/replifactory.experiment.MorbidostatExperiment/runs/20240620_114735/reactor-2.csv

## Processes

### Run new experiment

1. Select experiment class
2. Load or create preset (optional)
3. Fill required parameters
4. Run experiment
5. Store measurments
6. Sampling reactor (optional)
7. Stop experiment

### Restore experiments on software failure

1. Load unfinished experiment
2. Reconnect to machine with specific serial number
3. Continue experiment
4. ...
