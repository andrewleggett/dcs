import sys
import dcs
import dcs.mission
import dcs.task
import dcs.mapping
import dcs.terrain
import dcs.unittype
import dcs.vehicles
import random
import argparse
import os
from typing import List, Dict, Tuple


class USPlatoon:
    units = [
        dcs.countries.USA.Vehicle.Armor.APC_M1043_HMMWV_Armament,
        dcs.countries.USA.Vehicle.Armor.APC_M1043_HMMWV_Armament,
        dcs.countries.USA.Vehicle.Armor.APC_M1126_Stryker_ICV,
        dcs.countries.USA.Vehicle.AirDefence.AAA_Vulcan_M163
    ]
    maybe = [
        dcs.countries.USA.Vehicle.AirDefence.SAM_Avenger_M1097
    ]


class BasicScenario:
    def __init__(self):
        self.m = dcs.mission.Mission()

        self.m.coalition["red"].swap_country(self.m.coalition["blue"], dcs.countries.Ukraine.name)

        self.red_airports = []  # type: List[Airport]
        self.blue_airports = []  # type: List[Airport]
        self.setup_airports()

    def setup_airports(self):
        caucasus = self.m.terrain  # type: dcs.terrain.Caucasus
        self.red_airports = caucasus.default_red_airports()
        for a in self.red_airports:
            self.setup_airport(a, "red", [dcs.vehicles.AirDefence.SAM_SA_19_Tunguska_2S6,
                                          dcs.vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka])

        self.blue_airports = caucasus.default_blue_airports()
        for a in self.blue_airports:
            self.setup_airport(a, "blue", [dcs.vehicles.AirDefence.SAM_Avenger_M1097,
                                                dcs.vehicles.AirDefence.AAA_Vulcan_M163])

    def setup_airport(self, airport: dcs.terrain.Airport, side: str, air_def_units: List[dcs.unittype.VehicleType]):
        airport.set_coalition(side)

        if not airport.civilian:
            x, y = airport.random_unit_zone().center()
            if airport.is_red():
                dcs.templates.VehicleTemplate.Russia.sa10_site(self.m, x, y, 180)
            elif airport.is_blue():
                dcs.templates.VehicleTemplate.USA.patriot_site(self.m, x, y, 330)
        else:
            slots = len(airport.parking_slots)
            airdef = int(round(random.random() + slots/20, 0))
            x, y = airport.random_unit_zone().random_int_point()
            if airdef:
                vg = self.m.vehicle_group(
                    self.m.country("Russia") if airport.is_red() else self.m.country("USA"),
                    airport.name + " Air Defense",
                    air_def_units[random.randrange(0, len(air_def_units))],
                    x, y, 180)

                for i in range(1, airdef):
                    _type = air_def_units[random.randrange(0, len(air_def_units))]
                    u = self.m.vehicle(airport.name + " Air Defense #" + str(i), _type)
                    vg.add_unit(u)
                vg.formation_scattered(random.randrange(0, 359))

        return airport

    def add_civil_airtraffic(self, planes=(10, 20), helicopters=(0, 10), hidden=True):
        p_count = random.randrange(planes[0], planes[1])
        h_count = random.randrange(helicopters[0], helicopters[1])

        c_count = 1

        def civil_flight(countries, airports):
            country_str = countries[random.randrange(0, len(countries))]
            country = self.m.country(country_str)

            airport = airports[random.randrange(0, len(airports))]

            transports = [x for x in country.planes if dcs.planes.plane_map[x].task_default == dcs.task.Transport]
            ptype = dcs.planes.plane_map[transports[random.randrange(0, len(transports))]]

            slots = airport.free_parking_slot(ptype.large_parking_slot, False)

            x = random.randrange(dcs.terrain.Caucasus.bounds.bottom+100*1000, dcs.terrain.Caucasus.bounds.top-100*1000)
            y = random.randrange(dcs.terrain.Caucasus.bounds.left+600*1000, dcs.terrain.Caucasus.bounds.right-130*1000)

            name = "Civil " + str(c_count)
            rand = random.random()
            if 0.3 < rand < 0.5 and slots:
                pg = self.m.plane_group_from_parking(country, name, ptype, airport, coldstart=random.getrandbits(1))
                pg.add_runway_waypoint(airport, distance=random.randrange(6000, 8000, 100))
                pg.add_waypoint(x, y, random.randrange(5000, 8000, 100), 400)
            elif 0.5 < rand and slots:
                pg = self.m.plane_group_from_parking(country, name, ptype, airport)
                pg.uncontrolled = True
            else:
                bound = dcs.mapping.Rectangle(dcs.terrain.Caucasus.bounds.top-100*1000,
                                              dcs.terrain.Caucasus.bounds.left+200*1000,
                                              dcs.terrain.Caucasus.bounds.bottom+100*1000,
                                              dcs.terrain.Caucasus.bounds.right-130*1000)
                x, y = bound.random_int_point()

                pg = self.m.plane_group_inflight(
                    country, name, ptype, x, y, random.randrange(5000, 8000, 100), 400)
                tmp = pg.add_waypoint(0, 0, pg.points[0].alt)
                wp = pg.add_runway_waypoint(airport, distance=random.randrange(6000, 8000, 100))
                heading = dcs.mapping.heading_between_points(wp.x, wp.y, x, y)
                x, y = dcs.mapping.point_from_heading(wp.x, wp.y, heading, 30*1000)
                tmp.x = x
                tmp.y = y
                pg.land_at(airport)
            pg.set_frequency(240)
            return pg

        def heli_transport_flight(countries, airports):
            country_str = countries[random.randrange(0, len(countries))]
            country = self.m.country(country_str)

            transports = [x for x in country.helicopters
                          if dcs.helicopters.helicopter_map[x].task_default == dcs.task.Transport]
            htype = dcs.helicopters.helicopter_map[transports[random.randrange(0, len(transports))]]

            start_airport = airports[random.randrange(0, len(airports))]
            rand = random.random()
            name = "Helicopter Transport " + str(c_count)
            if 0.7 < rand:
                bound = dcs.mapping.Rectangle.from_point(start_airport.x, start_airport.y, 100*1000)
                x, y = bound.random_int_point()
                hg = self.m.helicopter_group_inflight(
                    country, name, htype, x, y, random.randrange(800, 1500, 100), 200)
                hg.add_runway_waypoint(start_airport)
                hg.land_at(start_airport)
            elif 0.4 < rand < 0.7:
                hg = self.m.helicopter_group_from_parking(country, name, htype, start_airport)
                hg.uncontrolled = True
            else:
                dest_airport = None
                while True:
                    dest_airport = airports[random.randrange(0, len(airports))]
                    if dest_airport != start_airport:
                        break

                hg = self.m.helicopter_group_from_parking(
                    country, name, htype, start_airport, coldstart=random.getrandbits(1))
                hg.add_runway_waypoint(start_airport)
                hg.add_runway_waypoint(dest_airport)
                hg.land_at(dest_airport)
            return hg

        # red
        red_countries = [dcs.countries.Russia.name]
        for i in range(0, int(p_count / 2)):
            cf = civil_flight(red_countries, self.red_airports)
            cf.hidden = hidden
            cf.points[0].tasks.append(dcs.task.SetInvisibleCommand())
            c_count += 1

        for i in range(0, int(h_count / 2)):
            hf = heli_transport_flight(red_countries, self.red_airports)
            hf.hidden = hidden
            hf.points[0].tasks.append(dcs.task.SetInvisibleCommand())
            c_count += 1

        # blue
        blue_countries = [dcs.countries.USA.name, dcs.countries.Ukraine.name, dcs.countries.Georgia.name]
        for i in range(0, int(p_count / 2)):
            cf = civil_flight(blue_countries, self.blue_airports)
            cf.hidden = hidden
            cf.points[0].tasks.append(dcs.task.SetInvisibleCommand())
            c_count += 1

        for i in range(0, int(h_count / 2)):
            hf = heli_transport_flight(blue_countries, self.blue_airports)
            hf.hidden = hidden
            hf.points[0].tasks.append(dcs.task.SetInvisibleCommand())
            c_count += 1

    def add_uncontrolled_military_planes(self, airports: List[dcs.terrain.Airport],
                                         planes: List[Tuple[str, str, int]], hidden=True):

        g_idx = 1
        while planes:
            country, strtype, group_size = planes.pop()

            while True:
                airport = airports[random.randrange(0, len(airports))]

                ptype = dcs.planes.plane_map[strtype]
                slots = airport.free_parking_slots(ptype.large_parking_slot, False)
                if len(slots) >= group_size:
                    break

            c = self.m.country(country)
            pg = self.m.plane_group_from_parking(c, strtype + " Flight #" + str(g_idx),
                                                 ptype, airport, parking_slots=slots, group_size=group_size)
            pg.uncontrolled = True
            pg.hidden = hidden
            g_idx += 1

    def place_players(self, country, start, aircraft_types: List[str],
                      airports: List[dcs.terrain.Airport],
                      placement_rect,
                      group_size) -> List[dcs.unitgroup.PlaneGroup]:

        plane_groups = []
        for aircraft_type in aircraft_types:
            plane_type = dcs.planes.plane_map[aircraft_type]
            airport = airports[random.randrange(0, len(airports))]

            if start == "inflight":
                x1, y1 = placement_rect.random_int_point()
                pg = self.m.plane_group_inflight(
                    country, "Refueler", plane_type, x1, y1, random.randrange(2000, 5000, 100), group_size=group_size)
            elif start == "runway":
                pg = self.m.plane_group_from_runway(country, "Refueler", plane_type, airport, group_size=group_size)
            else:
                pg = self.m.plane_group_from_parking(
                    country, "Refueler", plane_type, airport, coldstart=start == "cold", group_size=group_size)
            plane_groups.append(pg)

        return plane_groups

    def save(self, filename, stats):
        self.m.save(filename, show_stats=stats)


class Refueling(BasicScenario):
    def __init__(self, aircraft_types: List[str], playercount: int, start: str):
        super(Refueling, self).__init__()

        self.add_civil_airtraffic(hidden=False)

        caucasus = self.m.terrain  # type: dcs.terrain.Caucasus

        usa = self.m.country(dcs.countries.USA.name)
        ukraine = self.m.country(dcs.countries.Ukraine.name)

        batumi = caucasus.batumi()
        vaziani = caucasus.vaziani()

        kutaisi = caucasus.kutaisi()
        kobuleti = caucasus.kobuleti()
        blue_military = [kutaisi, kobuleti]

        planes = [
            (dcs.countries.USA.name, dcs.countries.USA.Plane.F_16C_bl_52d, 4),
            (dcs.countries.USA.name, dcs.countries.USA.Plane.F_15E, 2),
            (dcs.countries.USA.name, dcs.countries.USA.Plane.F_A_18C, 4),
            (dcs.countries.Georgia.name, dcs.countries.Georgia.Plane.Su_25T, 4)
        ]

        self.add_uncontrolled_military_planes(blue_military, planes, False)

        frequency = 140
        orbit_rect = dcs.mapping.Rectangle(
            int(batumi.x + 120*1000), int(batumi.y - 100 * 1000), int(batumi.x), int(vaziani.y))

        x1, y1, heading, race_dist = Refueling.random_orbit(orbit_rect)
        awacs = self.m.awacs_flight(
            usa,
            "AWACS",
            plane_type=dcs.planes.E_3A,
            airport=None,
            x=x1, y=y1,
            race_distance=race_dist, heading=heading,
            altitude=random.randrange(4000, 5500, 100), frequency=frequency)

        self.m.escort_flight(usa, "AWACS Escort", dcs.planes.plane_map[dcs.countries.USA.Plane.F_15E], None, awacs, 2)

        x1, y1, heading, race_dist = Refueling.random_orbit(orbit_rect)
        refuel_net = self.m.refuel_flight(
            ukraine,
            "Tanker IL",
            dcs.planes.IL_78M,
            airport=None,
            x=x1, y=y1,
            race_distance=race_dist, heading=heading,
            altitude=random.randrange(4000, 5500, 100), frequency=frequency)

        x1, y1, heading, race_dist = Refueling.random_orbit(orbit_rect)
        refuel_rod = self.m.refuel_flight(
            usa,
            "Tanker KC",
            dcs.planes.KC_135,
            airport=None,
            x=x1, y=y1,
            race_distance=race_dist, heading=heading,
            altitude=random.randrange(4000, 5500, 100), frequency=frequency)

        player_groups = self.place_players(usa, start, aircraft_types, blue_military, orbit_rect, playercount)

        if start == "inflight":
            fuel_percent = 0.2
        else:
            fuel_percent = 0.3

        for pg in player_groups:
            airport = caucasus.airport_by_id(pg.points[0].airdrome_id)
            airport = airport if airport else blue_military[random.randrange(0, len(blue_military))]
            if start != "inflight":
                pg.add_runway_waypoint(airport)

            for u in pg.units:
                if playercount > 1:
                    u.set_client()
                else:
                    u.set_player()
                u.fuel *= fuel_percent

            if pg.units[0].unit_type in [dcs.planes.A_10C]:
                pg.add_waypoint(refuel_rod.points[1].x, refuel_rod.points[1].y, 4000)
            else:
                pg.add_waypoint(refuel_net.points[1].x, refuel_net.points[1].y, 4000)

            pg.add_runway_waypoint(airport)
            pg.land_at(airport)

        self.m.set_description_text("""Random generated refueling test mission.
{count} {type} are/is prepared for a refueling training mission.""".format(
            count=playercount, type=", ".join(aircraft_types)))
        self.m.set_description_bluetask_text("""Find your tanker and do a full refuel.
Afterwards land at your designated homebase.

AWACS and Tankers are reachable on {freq} Mhz VHF-AM.""".format(freq=frequency))

    @staticmethod
    def random_orbit(rect: dcs.mapping.Rectangle):
        x1 = random.randrange(rect.bottom, rect.top)
        sy = rect.left
        y1 = random.randrange(sy, rect.right)
        heading = 90 if y1 < (sy + (rect.right - sy) / 2) else 270
        heading = random.randrange(heading - 20, heading + 20)
        race_dist = random.randrange(80*1000, 120*1000)
        return x1, y1, heading, race_dist


class Scenario(BasicScenario):

    def __init__(self):
        super(Scenario, self).__init__()

        self.red_airforce = {
            dcs.planes.MiG_29A.id: 1,
            dcs.planes.Su_24M.id: 1,
            dcs.planes.Su_25T.id: 1,
            dcs.planes.A_50.id: 1}

        self.red_airforce_escort = [
            dcs.planes.MiG_29S
        ]

        self.red_helicopter = [
            dcs.helicopters.Mi_24V.id
        ]

        self.red_ground = {
            dcs.countries.Russia.Vehicle.Armor.MBT_T_80U: 8,
            dcs.countries.Russia.Vehicle.Armor.IFV_BMP_3: 10,
            dcs.countries.Russia.Vehicle.AirDefence.SAM_SA_9_Strela_1_9P31: 6
        }

        self.blue_ground = [
            USPlatoon,
            USPlatoon,
            USPlatoon,
            USPlatoon,
            USPlatoon,
            USPlatoon
        ]

        self.blue_targets = []  # list[dcs.group.VehicleGroup]

        caucasus = self.m.terrain  # type: dcs.terrain.Caucasus
        ukraine = self.m.country(dcs.countries.Ukraine.name)

        nalchik = self.m.terrain.nalchik()
        beslan = self.m.terrain.beslan()
        mozdok = caucasus.mozdok()
        sochi = caucasus.sochi()

        senaki = self.m.terrain.senaki()
        batumi = self.m.terrain.batumi()
        soganlug = self.m.terrain.soganlug()
        vaziani = caucasus.vaziani()

        usa = self.m.country("USA")
        self.distribute_ground(usa, senaki.x, senaki.y, senaki.x + 20*1000, senaki.y - 30*1000, self.blue_ground)

        awacs = self.m.awacs_flight(usa, "AWACS", dcs.planes.E_3A, vaziani, vaziani.x - 5000, vaziani.y - 70000, race_distance=120 * 1000, heading=270)
        self.m.escort_flight(usa, str(awacs.name) + " escort us", dcs.planes.F_16C_bl_52d, vaziani, awacs)
        refuel = self.m.refuel_flight(ukraine, "Tanker", dcs.planes.IL_78M, batumi, batumi.x + 40000, batumi.y + 30000, race_distance=80*1000, heading=90)

        patrol = self.m.patrol_flight(usa, "patrolium", dcs.planes.F_15C, soganlug,
                                      soganlug.x, soganlug.y - 20*1000, soganlug.x + 20*1000, soganlug.y - 200*1000)

        pg = self.m.plane_group_from_parking(usa, "Airgroup", dcs.planes.M_2000C, batumi)
        pg.units[0].set_player()
        pg.load_loadout("air2air")

        russia = self.m.country("Russia")
        self.distribute_air(russia, [sochi, mozdok, nalchik, caucasus.mineralnye()], self.red_airforce, self.red_airforce_escort)

    def distribute_ground(self, _country, x1, y1, x2, y2, groundforce):
        xmin = int(min(x1, x2))
        xmax = int(max(x1, x2))
        ymin = int(min(y1, y2))
        ymax = int(max(y1, y2))
        i = 0
        isblue = self.m.is_blue(_country)
        side = "Blue" if isblue else "Red"
        for uname in groundforce:
            x = random.randrange(xmin, xmax, 10)
            y = random.randrange(ymin, ymax, 10)
            units = list(uname.units)
            if random.randrange(0, 100) > 80:
                units += uname.maybe
            vg = self.m.vehicle_group_platoon(_country, side + " " + str(uname.__name__) + " " + str(i), units, x, y, random.randrange(0, 359))
            vg.formation_scattered()
            if isblue:
                self.blue_targets.append(vg)
            i += 1

    def distribute_air(self, _country, airports, airforce, escort):
        air_distr = dict(airforce)
        escort_distr = list(escort)

        isblue = self.m.is_blue(_country)
        if isblue:
            ground_targets = self.red_targets
        else:
            ground_targets = self.blue_targets
        i = 100
        while sum([air_distr[x] for x in air_distr]) > 0:
            port = random.randrange(len(airports))

            types = [x for x in airforce if air_distr[x] > 0]

            print(types)
            _type_id = types[random.randrange(len(types))]

            _type = dcs.planes.plane_map[_type_id]
            if not airports[port].free_parking_slot(_type.large_parking_slot, False):
                continue

            airport = airports[port]
            if airport.name == "Nalchik":
                airports.pop(port)

            if _type.task_default == dcs.task.AWACS:
                if self.m.is_red(_country):
                    sochi = self.m.terrain.sochi()
                    x = random.randrange(int(sochi.x + 20*1000), -10000)
                    y = sochi.y + random.randrange(20000, 50000)

                awacs = self.m.awacs_flight(_country, "AWACS", _type, airport, x, y, random.randrange(30*1000, 120*1000), random.randrange(60, 110), random.randrange(3800, 5000))

                if escort_distr:
                    escort_type = escort_distr.pop()
                    self.m.escort_flight(_country, str(awacs.name) + " escort", escort_type, airport, awacs, group_size=2)
            elif _type.task_default in [dcs.task.CAS, dcs.task.GroundAttack]:
                target = ground_targets[random.randrange(0, len(ground_targets))]

                if True:
                    if airport.runway_free:
                        pg = self.m.plane_group_from_runway(_country, "Airgroup " + str(i), _type, airport, maintask=dcs.task.CAS, group_size=2)
                    else:
                        pg = self.m.plane_group_from_parking(_country, "Airgroup " + str(i), _type, airport, maintask=dcs.task.CAS, group_size=2)
                    last_wp = pg.add_runway_waypoint(airport)
                else:
                    heading = int(dcs.mapping.heading_between_points(target.x(), target.y(), airport.x, airport.y) + 360)
                    heading = random.randrange(heading - 20, heading + 20) - 360
                    x, y = dcs.mapping.point_from_heading(target.x(), target.y(), heading, random.randrange(50, 80)*1000)
                    pg = self.m.plane_group_inflight(_country, "Airgroup " + str(i), _type, x, y, 1000, maintask=dcs.task.CAS, group_size=2)
                    last_wp = pg.points[0]
                pg.points[0].tasks.clear()
                pg.points[0].tasks.append(dcs.task.EngageTargets(20*1000, [dcs.task.Targets.All.GroundUnits.GroundVehicles]))

                if _type == dcs.planes.Su_25T:
                    pg.load_loadout("APU-8 Vikhr-M*2,S-25L*2,R-73*2,SPPU-22*2,Mercury LLTV Pod,MPS-410")

                heading = dcs.mapping.heading_between_points(last_wp.x, last_wp.y, target.x(), target.y())
                distance = dcs.mapping.distance(last_wp.x, last_wp.y, target.x(), target.y())
                x, y = dcs.mapping.point_from_heading(last_wp.x, last_wp.y, heading, distance - 5000)
                last_wp = pg.add_waypoint(x, y, 4000)
                last_wp.tasks.append(dcs.task.CAS.EnrouteTasks.EngageGroup(target.id))
                pg.add_waypoint(last_wp.x + 1000 * 10, last_wp.y, 4000)
                pg.add_runway_waypoint(airport)
                pg.land_at(airport)
            else:
                pg = self.m.plane_group_from_parking(_country, "Airgroup " + str(i), _type, airport, group_size=2)
                if pg.task == dcs.task.CAP.name:
                    pg.points[0].tasks.clear()
                    pg.points[0].tasks.append(dcs.task.CAP.EnrouteTasks.EngageTargets(50*1000, [dcs.task.Targets.All.Air.Planes]))

                last_wp = pg.add_runway_waypoint(airport)

                hdg = 230
                waypoints = 5
                for i in range(0, waypoints):
                    if i > waypoints - 3:
                        hdg = (hdg + 180) % 360
                    hdg = random.randrange(hdg - 70, hdg + 70)
                    x, y = dcs.mapping.point_from_heading(last_wp.x, last_wp.y, hdg, random.randrange(10*1000, 60*1000, 1000))
                    last_wp = pg.add_waypoint(x, y, 4000)

                pg.add_runway_waypoint(airport)
                pg.land_at(airport)

            air_distr[_type_id] -= 1
            i += 1


def main():

    parser = argparse.ArgumentParser(description="Random DCS mission generator")

    parser.add_argument("-a", "--aircrafttype", default=dcs.planes.Su_25T.id,
                        choices=[
                            dcs.planes.A_10C.id,
                            dcs.planes.Su_25T.id,
                            dcs.planes.M_2000C.id,
                            dcs.helicopters.Ka_50.id],
                        help="Player aircraft type")
    parser.add_argument("-p", "--playercount", default=1, type=int)
    parser.add_argument("-s", "--start", default="inflight", choices=["inflight", "runway", "warm", "cold"])
    parser.add_argument("-t", "--missiontype", default="main", choices=["main", "CAS", "CAP", "refuel"])
    parser.add_argument("--show-stats", action="store_true", default=False, help="Show generated missions stats")
    parser.add_argument("-o", "--output", default=os.path.join(os.path.expanduser("~"), "Saved Games\\DCS\\Missions\\random.miz"))

    args = parser.parse_args()
    missiontype = args.missiontype
    if args.aircrafttype in [dcs.planes.Su_25T.id, dcs.helicopters.Ka_50.id]:
        missiontype = "CAS"
    if args.aircrafttype == dcs.planes.A_10C.id:
        if args.missiontype not in ["CAS", "refuel"]:
            missiontype = "CAS"

    if missiontype == "refuel":
        supported = [dcs.planes.A_10C.id, dcs.planes.M_2000C.id]
        aircraft_types = supported if args.playercount > 1 else [args.aircrafttype]
        s = Refueling(aircraft_types, args.playercount, args.start)
    else:
        s = Scenario()

    s.save(args.output, args.show_stats)


if __name__ == '__main__':
    sys.exit(main())
