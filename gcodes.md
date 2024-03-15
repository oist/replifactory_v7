# G-Codes for replifactory v5

## Experiment commands

- Stirrer V<vial> S<speed>
- Stop stirring V<vial>
- Measure optical density V<vial> [L<laser>]
- Measure temperature T<thermometer>
- Pump P<pump> S<speed> [V<volume>] V<vial>
- Stop pumping P<pump>

## Devices

M101 P1 S<speed> [V<volume>] ; pump liquid from Pump 1, where <speed> is the desired flow rate in milliliters per minute and <volume> is desired volume in milliliters
M102 P1 ; stop pumping
M103 V1 ; open valve 1
M104 V1 ; close valve 1
M105 S1 R<speed> ; stir with stirrer 1 where <speed> is desired rotation speed in revolution per minute
M106 S1 ; stop stirring with stirrer 1
M107 O1 ; measure optical density with sensor 1 and read the value from the serial output
M108 T1 ; measure temperature with thermometer 1 and read the value from the serial output

Action:
    Name: Add 10ml drug to vial 5
    Commands:
      - soft stop main pump:
        Instructions:
          - motor driver 1 stop
          - motor driver 1 read status
      - wait until main pump stoped
        Repeat until status OPERATIONAL or ERROR
        Instructions:
          - motor driver 1 read status
      - soft stop drug pump
        Instructions:
          - motor driver 2 stop
          - motor driver 2 read status
      - wait until pump 2 stoped
        Repeat until status OPERATIONAL or ERROR
        Instructions:
          - motor driver 2 read status
      - soft stop waste pump
        Instructions:
          - motor driver 4 stop
          - motor driver 4 read status
      - wait until pump 4 stoped
        Repeat until status OPERATIONAL ot ERROR
        Instructions:
          - motor driver 4 read status
      - close vial 1 valve
        Instructions:
          - valve pwm driver channel for valve 1 close signal
      - close vial 2 valve
      - close vial 3 valve
      - close vial 4 valve
      - close vial 6 valve
      - close vial 7 valve
      - close vial N valve
      - open vial 5 valve
      - wait X ms to be sure that all valves change state
      - run main pump for 10 ml
      - wait until main pump finished

read od: N
- select vial: N
- sleep 1ms
- read adc -> A
- laser on
- sleep 1ms
- read adc -> B
- laser off
- return normalize(B - A)

reset state

toggle: OBJ [STATE]
toggle: laserN ON
toggle: laserN

turn on laser: N
- select vial: N
- laser on


PAL - Parallel Action Language (Working Title)

Entities:
- stepper (STATE)
- thermometer (STATE)
- toggle (STATE)
  - "callback"
- laser (toggle/2)
- stirrer
- adc (STATE)

Entities (Gen2):
- pump (stepper)
- optical_density_sensor (adc laser)
- container
  - pipe*
- vial (container)
- reactor (vial stirrer optical_density_sensor)
  - from* (pipe)
  - vial
  - to (pipe)
- tank (container)
  - from/to (pipe)
- pipe (toggle/N pump)
  - from (container)
  - pump
  - to* (container, toggle/N)
    - valve
- valve (toggle/2)
  - pipe*

Actions:
- toggle: TARGET [STATE] [@ <runtime-handler>]
    # Example 1
    #    toggle: valve1 open
    #      then block
    #      timeout 100ms :
    #          toggle: warning
    #          toggle: e-stop
    # Example 2
    #    toggle: valve1 open
    #      then block
    #      timeout 100ms stuck
    #    ...
    #    wait: stuck:
    #      toggle: warning
    #      toggle: e-stop
- wait: ID [GROUP]
- timeout: ID TIME [GROUP]
- abort: ID
- set: TARGET [KEY] VALUE
- get: TARGET [KEY]
- stepper.run: TARGET DIRECTION [N] [SPEED_PROFILE] [@ <runtime-handler>]
  # Example
  # stepper.run: pump1 cw 1L slow
  #   then fill
  #   timeout 1h :
  #     stepper.stop: pump1
  #     toggle: error_state
  # ...
  # wait: fill:
  #   ...
  # ...
  # wait: fill
  # ...
- stepper.stop: TARGET [MODE] [@ <runtime-handler>]
- stirrer.run: TARGET SPEED [@ <runtime-handler>]
- stirrer.stop: TARGET [@ <runtime-handler>]

<runtime-handler> ::= [then "block"|ID|GROUP [timeout TIMEOUT [ID|GROUP]] ]

Meta actions:
- <priority-action> ::= ! <action>
- <group> ::= : \n <actions>
- <actions> ::= <indent><action> [<actions>]
- <named-group> ::= <name> = <args> <group>
  # Example
  #   func = a b=1 :
  #     toggle: a b
- <args> ::= <name>[=<value>] [<args>]
- <python-expr> ::= { <python-code> }
- <while-loop> -- as in python
- <conditionals> -- as in python
- <variables> -- as in python

Runtime:
- FrameStack
  - Queue
- PriorityFrameStack (FrameStack)
- HandlerMap
- TimeoutQueue

Interpretation:
- pop from top queue in stack
  - if command
    register done id/group
    register timeout id/group
  - if group -> push to queue
- on timeout
  - if group handler -> push to queue
