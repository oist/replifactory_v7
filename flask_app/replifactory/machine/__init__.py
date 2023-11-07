class MachineInterface:
    @classmethod
    def get_connection_options(cls, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        pass

    def disconnect(self, *args, **kwargs):
        raise NotImplementedError()

    def get_transport(self):
        raise NotImplementedError()

    def health_check(self):
        raise NotImplementedError()

    def commands(self, commands, force=False, *args, **kwargs):
        raise NotImplementedError()

    def experiment(self, experiment, *args, **kwargs):
        raise NotImplementedError()

    def start_experiment(self):
        raise NotImplementedError()

    def pause_experiment(self):
        raise NotImplementedError()

    def resume_experiment(self):
        raise NotImplementedError()

    def togle_pause_experiment(self):
        if self.is_running():
            self.pause_experiment()
        elif self.is_paused():
            self.resume_experiment()

    def cancel_experiment(self):
        raise NotImplementedError()

    def get_state_string(self, *args, **kwargs):
        raise NotImplementedError()

    def get_state_id(self, *args, **kwargs):
        pass

    def get_current_data(self, *args, **kwargs):
        raise NotImplementedError()

    def get_current_job(self, *args, **kwargs):
        raise NotImplementedError()

    def get_current_temperatures(self, *args, **kwargs):
        """
        Returns:
            (dict) The current temperatures.
        """
        raise NotImplementedError()

    def get_temperature_history(self, *args, **kwargs):
        """
        Returns:
            (list) The temperature history.
        """
        raise NotImplementedError()

    def get_current_connection(self, *args, **kwargs):
        raise NotImplementedError()

    def is_closed_or_error(self, *args, **kwargs):
        """
        Returns:
            (boolean) Whether the machine is currently disconnected and/or in an error state.
        """
        raise NotImplementedError()

    def is_operational(self, *args, **kwargs):
        """
        Returns:
            (boolean) Whether the machine is currently connected and available.
        """
        raise NotImplementedError()

    def is_running(self):
        pass

    def is_cancelling(self, *args, **kwargs):
        """
        Returns:
            (boolean) Whether the machine is currently cancelling an experiment.
        """
        raise NotImplementedError()

    def is_pausing(self, *args, **kwargs):
        """
        Returns:
                (boolean) Whether the machine is currently pausing an experiment.
        """
        raise NotImplementedError()

    def is_paused(self, *args, **kwargs):
        """
        Returns:
            (boolean) Whether the machine is currently paused.
        """
        raise NotImplementedError()

    def is_error(self, *args, **kwargs):
        """
        Returns:
            (boolean) Whether the machine is currently in an error state.
        """
        raise NotImplementedError()

    def is_ready(self, *args, **kwargs):
        """
        Returns:
            (boolean) Whether the machine is currently operational and ready for new experiment jobs (not running).
        """
        raise NotImplementedError()

    def register_callback(self, callback, *args, **kwargs):
        """
        Registers a :class:`MachineCallback` with the instance.

        Arguments:
            callback (MachineCallback): The callback object to register.
        """
        raise NotImplementedError()

    def unregister_callback(self, callback, *args, **kwargs):
        """
        Unregisters a :class:`MachineCallback` from the instance.

        Arguments:
            callback (MachineCallback): The callback object to unregister.
        """
        raise NotImplementedError()

    def send_initial_callback(self, callback):
        """
        Sends the initial printer update to :class:`MachineCallback`.

        Arguments:
                callback (MachineCallback): The callback object to send initial data to.
        """
        raise NotImplementedError()

    @property
    def firmware_info(self):
        raise NotImplementedError()


class MachineCallback:
    def on_machine_add_log(self, data):
        pass

    def on_machine_add_temperature(self, data):
        pass

    def on_machine_add_optical_density(self, data):
        pass

    def on_machine_send_initial_data(self, data):
        pass

    def on_machine_send_current_data(self, data):
        """
        Called when the internal state of the :class:`MachineInterface` changes, due to changes in the printer state,
        temperatures, log lines, job progress etc. Updates via this method are guaranteed to be throttled to a maximum
        of 2 calls per second.

        ``data`` is a ``dict`` of the following structure::

            state:
                text: <current state string>
                flags:
                    operational: <whether the printer is currently connected and responding>
                    printing: <whether the printer is currently printing>
                    closedOrError: <whether the printer is currently disconnected and/or in an error state>
                    error: <whether the printer is currently in an error state>
                    paused: <whether the printer is currently paused>
                    ready: <whether the printer is operational and ready for jobs>
                    sdReady: <whether an SD card is present>
            job:
                file:
                    name: <name of the file>,
                    size: <size of the file in bytes>,
                    origin: <origin of the file, "local" or "sdcard">,
                    date: <last modification date of the file>
                estimatedPrintTime: <estimated print time of the file in seconds>
                lastPrintTime: <last print time of the file in seconds>
                filament:
                    length: <estimated length of filament needed for this file, in mm>
                    volume: <estimated volume of filament needed for this file, in ccm>
            progress:
                completion: <progress of the print job in percent (0-100)>
                filepos: <current position in the file in bytes>
                printTime: <current time elapsed for printing, in seconds>
                printTimeLeft: <estimated time left to finish printing, in seconds>
            currentZ: <current position of the z axis, in mm>
            offsets: <current configured temperature offsets, keys are "bed" or "tool[0-9]+", values the offset in degC>

        Arguments:
            data (dict): The current data in the format as specified above.
        """
        pass
