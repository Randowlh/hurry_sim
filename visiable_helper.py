import ephem
import astropy.units as u
import distant_tools
class Visible_time_helper:
    def __init__(self, ground_stations,satellites,max_gsl_length_m,epoch,time_step, sim_duration):
        self.epoch =epoch
        # # 输入单位为 ms，需转化为 s
        self.time_step = time_step
        self.sim_duration = sim_duration
        # super().__init__(epoch,time_step, sim_duration)
        self.max_gsl_length_m = max_gsl_length_m
        visible_times = {}
        for gid in range(len(ground_stations)):
            print(gid,"的可见卫星计算中")
            visible_times[gid] = {}
            for sid in range(len(satellites)):
                visible_time = self.calculate_visible_time(satellites[sid], ground_stations[gid])
                visible_times[gid][sid] = visible_time
        self.visible_times = visible_times

    def calculate_visible_time(self, satellite, ground_station):
        i = 0
        visible_flag = False
        while i <= self.sim_duration:
            now=self.epoch + i * u.ns
            distant= distant_tools.distance_m_ground_station_to_satellite(ground_station,satellite,str(self.epoch),str(now))
            if distant< self.max_gsl_length_m:  # 检查卫星的仰角是否大于最小仰角
                visible_flag = True
                start = now
                break
            else:
                i = i + self.time_step

        if visible_flag:
            while i <= self.sim_duration:
                now=self.epoch + i * u.ns
                distant= distant_tools.distance_m_ground_station_to_satellite(ground_station,satellite,str(self.epoch),str(now))
                if distant < self.max_gsl_length_m:  # 检查卫星的仰角是否大于最小仰角
                    end = now
                    i = i + self.time_step
                else:
                    break
            return [start, end]    
        else:
            return [self.epoch, self.epoch]

