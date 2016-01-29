import zipfile
import lua


class String:
    def __init__(self, _id='', translation=None, lang='DEFAULT'):
        self.translation = translation
        self.lang = lang
        self._id = _id

    def set(self, text):
        self.translation.set_string(self._id, text, self.lang)
        return str(self)

    def id(self):
        return self._id

    def __str__(self):
        return self.translation.strings[self.lang][self._id]

    def __repr__(self):
        return self._id + ":" + str(self)


class Translation:
    def __init__(self):
        self.strings = {}
        self.maxDictId = 0

    def set_string(self, _id, string, lang='DEFAULT'):
        if lang not in self.strings:
            self.strings[lang] = {}
        self.strings[lang][_id] = string
        return _id

    def get_string(self, _id, lang='DEFAULT'):
        return String(_id, self, lang)

    def set_max_dict_id(self, dict_id):
        self.maxDictId = dict_id

    def max_dict_id(self):
        return self.maxDictId

    def __str__(self):
        return str(self.strings)

    def __repr__(self):
        return repr(self.strings)


class Options:
    def __init__(self, opts={}):
        self.options = opts

    def __repr__(self):
        return repr(self.options)


class Wind:
    def __init__(self, direction=0, speed=0):
        self.direction = direction
        self.speed = speed

    def dict(self):
        return {"speed": self.speed, "dir": self.direction}


class Cyclone:
    def __init__(self):
        self.pressure_spread = 0.0
        self.centerZ = 0.0
        self.ellipticity = 0.0
        self.rotation = 0.0
        self.pressure_excess = 0
        self.centerX = 0.0

    def dict(self):
        d = {
            "pressure_spread": self.pressure_spread,
            "pressure_excess": self.pressure_excess,
            "centerZ": self.centerZ,
            "ellipticity": self.ellipticity,
            "rotation": self.rotation,
            "centerX": self.centerX
        }
        return d


class Weather:
    def __init__(self):
        self.atmosphere_type = 0
        self.wind_at_ground = Wind()
        self.wind_at_2000 = Wind()
        self.wind_at_8000 = Wind()
        self.enable_fog = False
        self.turbulence_at_ground = 0
        self.turbulence_at_2000 = 0
        self.turbulence_at_8000 = 0
        self.season_temperature = 20
        self.season_iseason = 1
        self.type_weather = 0
        self.qnh = 760
        self.cyclones = []
        self.name = "Summer, clean sky"
        self.fog_thickness = 0
        self.fog_visibility = 25
        self.fog_density = 7
        self.visibility_distance = 80000
        self.clouds_thickness = 200
        self.clouds_density = 0
        self.clouds_base = 300
        self.clouds_iprecptns = 0

    def dict(self):
        d = {}
        d["atmosphere_type"] = self.atmosphere_type
        d["wind"] = {"atGround": self.wind_at_ground.dict(),
                     "at2000": self.wind_at_2000.dict(),
                     "at8000": self.wind_at_8000.dict()}
        d["enable_fog"] = self.enable_fog
        d["turbulence"] = {"atGround": self.turbulence_at_ground,
                           "at2000": self.turbulence_at_2000,
                           "at8000": self.turbulence_at_8000}
        d["season"] = {"iseason": self.season_iseason, "temperature": self.season_temperature}
        d["type_weather"] = self.type_weather
        d["qnh"] = self.qnh
        d["cyclones"] = {x: self.cyclones[x] for x in range(0, len(self.cyclones))}
        d["name"] = self.name
        d["fog"] = {"thickness": self.fog_thickness, "visibility": self.fog_visibility, "density": self.fog_density}
        d["visibility"] = {"distance": self.visibility_distance}
        d["clouds"] = {"thickness": self.clouds_thickness,
                       "density": self.clouds_density,
                       "base": self.clouds_base,
                       "iprecptns": self.clouds_iprecptns}
        return d


class Task:
    CAS = "CAS"
    CAP = "CAP"


class VehicleType:
    M818 = "M 818"


class PlaneType:
    A10C = "A-10C"


class Skill:
    AVERAGE = "Average"
    HIGH = "High"


class MapPosition:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y


class Unit:
    def __init__(self, id=None, name=None, type=""):
        self.type = ""
        self.x = 0
        self.y = 0
        self.heading = 0
        self.id = id
        self.skill = Skill.AVERAGE
        self.name = name if name else String()

    def set_position(self, pos):
        self.x = pos.x()
        self.y = pos.y()

    def dict(self):
        d = {}
        d["type"] = self.type
        d["x"] = self.x
        d["y"] = self.y
        d["heading"] = self.heading
        d["skill"] = self.skill
        d["unitId"] = self.id
        d["name"] = self.name.id()
        return d


class Vehicle(Unit):
    def __init__(self, id=None, name=None, type=""):
        super(Vehicle, self).__init__(id, name, type)
        self.player_can_drive = False
        self.transportable = {"randomTransportable": False}

    def dict(self):
        d = super(Vehicle, self).dict()
        print(self.player_can_drive)
        d["playerCanDrive"] = self.player_can_drive
        d["transportable"] = self.transportable
        return d


class Plane(Unit):
    def __init__(self, id=None, name=None, type=""):
        super(Plane, self).__init__(id, name, type)
        self.livery_id = ""
        self.parking = None
        self.psi = ""
        self.onboard_num = "010"
        self.alt = 0
        self.alt_type = "BARO"
        self.flare = 0
        self.chaff = 0
        self.fuel = 0
        self.gun = 0
        self.ammo_type = 0
        self.pylons = {}
        self.callsign_name = ""
        self.callsign = [1, 1, 1]

    def dict(self):
        d = super(Plane, self).dict()
        d["livery_id"] = self.livery_id
        d["psi"] = self.psi
        d["onboard_num"] = self.onboard_num
        d["payload"] = {
            "flare": self.flare,
            "chaff": self.chaff,
            "fuel": self.fuel,
            "gun": self.gun,
            "ammo_type": self.ammo_type,
            "pylons": self.pylons
        }
        d["callsign"] = {
            "name": self.callsign_name,
            1: self.callsign[0],
            2: self.callsign[1],
            3: self.callsign[2]
        }
        return d


class StaticType:
    AMMUNITION_DEPOT = ".Ammunition depot"


class Static(Unit):
    def __init__(self):
        self.category = "Warehouses"
        self.can_cargo = False


class Point:
    def __init__(self):
        self.alt = 0
        self.alt_type = "BARO"
        self.type = ""
        self.name = String()
        self.ETA = 0
        self.ETA_locked = True
        self.formation_template = ""
        self.speed_locked = True
        self.x = 0
        self.y = 0
        self.speed = 0
        self.action = "Offroad"
        self.task = {}
        self.properties = None

    def dict(self):
        d = {}
        d["alt"] = self.alt
        d["alt_type"] = self.alt_type
        d["type"] = self.type
        d["name"] = self.name.id()
        d["ETA"] = self.ETA
        d["ETA_locked"] = self.ETA_locked
        d["speed"] = self.speed
        d["speed_locked"] = self.speed_locked
        d["formation_template"] = self.formation_template
        d["x"] = self.x
        d["y"] = self.y
        d["action"] = self.action
        d["task"] = self.task
        return d


class Group:
    def __init__(self, name=None):
        self.tasks = []
        self.uncontrolled = False
        self.id = 0
        self.hidden = False
        self.visible = False
        self.units = []
        self.x = 0
        self.y = 0  # for now take pos from first unit
        self.spans = []
        self.points = []
        self.name = name if name else String()
        self.frequency = None

    def add_unit(self, unit: Unit):
        self.units.append(unit)

    def add_point(self, point: Point):
        self.points.append(point)

    def add_span(self, pos):
        self.spans.append({"x": pos.x, "y": pos.y})

    def dict(self):
        d = {}
        d["visible"] = self.visible
        d["hidden"] = self.hidden
        d["name"] = self.name.id()
        d["groupId"] = self.id
        if self.units:
            d["x"] = self.units[0].x
            d["y"] = self.units[0].y
            d["units"] = {}
            i = 1
            for unit in self.units:
                d["units"][i] = unit.dict()
        if self.points:
            d["route"] = {"points": {}}
            i = 1
            for point in self.points:
                d["route"]["points"][i] = point.dict()
                i += 1
        if self.spans:
            d["route"]["spans"] = {}
            i = 1
            for spawn in self.spans:
                d["route"]["spans"][i] = spawn
                i += 1
        return d


class MovingGroup(Group):
    def __init__(self, task="", name=None, start_time=0):
        super(MovingGroup, self).__init__(name)
        self.task = task
        self.start_time = start_time

    def dict(self):
        d = super(MovingGroup, self).dict()
        d["task"] = self.task
        d["start_time"] = self.start_time
        return d


class VehicleGroup(MovingGroup):
    def __init__(self, task="", name=None, start_time=0):
        super(VehicleGroup, self).__init__(task, name, start_time)
        self.modulation = 0
        self.frequency = 251
        self.communication = True

    def dict(self):
        d = super(VehicleGroup, self).dict()
        d["modulation"] = self.modulation
        d["frequency"] = self.frequency
        d["communication"] = self.communication
        return d


class PlaneGroup(MovingGroup):
    def __init__(self, task="", name=None, start_time=0):
        super(PlaneGroup, self).__init__(task, name, start_time)
        self.modulation = 0
        self.frequency = 251
        self.communication = True

    def dict(self):
        d = super(PlaneGroup, self).dict()
        d["modulation"] = self.modulation
        d["frequency"] = self.frequency
        d["communication"] = self.communication
        return d


class StaticGroup(Group):
    def __init__(self, task="", name=None, start_time=0):
        super(StaticGroup, self).__init__(task, name, start_time)
        self.dead = False
        self.heading = 0

    def dict(self):
        d = super(StaticGroup, self).dict()
        d["dead"] = self.dead
        d["heading"] = self.heading
        return d


class Country:
    def __init__(self, _id, name, vehicle_group=None, plane_group=None, static_group=None):
        self.id = _id
        self.name = name
        self.vehicle_group = vehicle_group if vehicle_group else []
        self.plane_group = plane_group if plane_group else []
        self.static_group = static_group if static_group else []

    def name(self):
        return self.name

    def add_vehicle_group(self, vgroup):
        self.vehicle_group.append(vgroup)

    def add_plane_group(self, pgroup):
        self.plane_group.append(pgroup)

    def add_static_group(self, sgroup):
        self.static_group.append(sgroup)

    def dict(self):
        d = {}
        d["name"] = self.name
        d["id"] = self.id

        if self.vehicle_group:
            d["vehicle"] = {"group": {}}
            i = 1
            for vgroup in self.vehicle_group:
                d["vehicle"]["group"][i] = vgroup.dict()
                i += 1
        if self.plane_group:
            d["plane"] = {"group": {}}
            i = 1
            for plane_group in self.plane_group:
                d["plane"]["group"][i] = plane_group.dict()
                i += 1

        if self.static_group:
            d["static"] = {"group": {}}
            i = 1
            for static_group in self.static_group:
                d["static"]["group"][i] = static_group.dict()
                i += 1
        return d

    def __str__(self):
        return str(self.id) + "," + self.name + "," + str(self.vehicle_group)


class Coalition:
    def __init__(self, name, bullseye=None):
        self.name = name
        self.countries = []
        self.bullseye = bullseye
        self.nav_points = []

    def set_bullseye(self, bulls):
        self.bullseye = bulls

    def add_country(self, country):
        self.countries.append(country)

    def remove_country(self, name):
        return self.countries.pop(name)

    def dict(self):
        d = {}
        d["name"] = self.name
        if self.bullseye:
            d["bullseye"] = self.bullseye
        d["country"] = {}
        i = 1
        for country in self.countries:
            d["country"][i] = country.dict()
            i += 1
        d["nav_points"] = {}
        return d


class Mission:
    trig = {}
    triggers = {}
    result = {}
    groundControl = {}
    usedModules = {}
    resourceCounter = {}
    weather = Weather()
    needModules = {}
    COUNTRY_IDS = [x for x in range(0, 47)]

    options = Options()
    forcedOptions = {}
    failures = {}

    def __init__(self):
        self.translation = Translation()

        self.description_text = String()
        self.description_bluetask = String()
        self.description_redtask = String()
        self.sortie = String()
        self.pictureFileNameR = ""
        self.pictureFileNameB = ""
        self.version = 9
        self.currentKey = 0
        self.start_time = 43200
        self.theatre = "Caucasus"
        self.goals = {}
        self.coalition = {}

        self.usedModules = {
            'Su-25A by Eagle Dynamics': True,
            'MiG-21Bis AI by Leatherneck Simulations': True,
            'UH-1H Huey by Belsimtek': True,
            'Su-25T by Eagle Dynamics': True,
            'F-86F Sabre by Belsimtek': True,
            'Su-27 Flanker by Eagle Dynamics': True,
            'Hawk T.1A AI by VEAO Simulations': True,
            'MiG-15bis AI by Eagle Dynamics': True,
            'Ka-50 Black Shark by Eagle Dynamics': True,
            'Combined Arms by Eagle Dynamics': True,
            'L-39C/ZA by Eagle Dynamics': True,
            'A-10C Warthog by Eagle Dynamics': True,
            'F-5E/E-3 by Belsimtek': True,
            'C-101 Aviojet': True,
            'TF-51D Mustang by Eagle Dynamics': True,
            './CoreMods/aircraft/MQ-9 Reaper': True,
            'C-101 Aviojet by AvioDev': True,
            'P-51D Mustang by Eagle Dynamics': True,
            'A-10A by Eagle Dynamics': True,
            'World War II AI Units by Eagle Dynamics': True,
            'MiG-15bis by Belsimtek': True,
            'F-15C': True,
            'Flaming Cliffs by Eagle Dynamics': True,
            'Bf 109 K-4 by Eagle Dynamics': True,
            'Mi-8MTV2 Hip by Belsimtek': True,
            'MiG-21Bis by Leatherneck Simulations': True,
            'M-2000C by RAZBAM Sims': True,
            'FW-190D9 Dora by Eagle Dynamics': True,
            'Caucasus': True,
            'Hawk T.1A by VEAO Simulations': True,
            'F-86F Sabre AI by Eagle Dynamics': True
        }

    def _import_point(self, group: Group, imp_group) -> Group:
        for imp_point_idx in imp_group["route"]["points"]:
            imp_point = imp_group["route"]["points"][imp_point_idx]
            point = Point()
            point.alt = imp_point["alt"]
            point.alt_type = imp_point["alt_type"]
            point.type = imp_point["type"]
            point.x = imp_point["x"]
            point.y = imp_point["y"]
            point.action = imp_point["action"]
            point.ETA_locked = imp_point["ETA_locked"]
            point.ETA = imp_point["ETA"]
            point.formation_template = imp_point["formation_template"]
            point.speed_locked = imp_point["speed_locked"]
            point.speed = imp_point["speed"]
            point.name = self.translation.get_string(imp_point["name"])
            point.task = imp_point["task"]
            group.add_point(point)
        return group

    def load_file(self, filename):
        mission_dict = {}
        options_dict = {}
        warehouse_dict = {}
        dictionary_dict = {}

        def loaddict(fname, miz):
            with miz.open(fname) as mfile:
                data = mfile.read()
                data = data.decode()
                return lua.loads(data)

        with zipfile.ZipFile(filename, 'r') as miz:
            mission_dict = loaddict('mission', miz)
            options_dict = loaddict('options', miz)
            warehouse_dict = loaddict('warehouses', miz)
            dictionary_dict = loaddict('l10n/DEFAULT/dictionary', miz)

        imp_mission = mission_dict["mission"]

        # import translations
        self.translation = Translation()
        translation_dict = dictionary_dict["dictionary"]
        for sid in translation_dict:
            self.translation.set_string(sid, translation_dict[sid], 'DEFAULT')

        self.translation.set_max_dict_id(imp_mission["maxDictId"])

        # print(self.translation)

        # import options
        self.options = Options(options_dict["options"])

        # import base values
        self.description_text = self.translation.get_string(imp_mission["descriptionText"])
        self.description_bluetask = self.translation.get_string(imp_mission["descriptionBlueTask"])
        self.description_redtask = self.translation.get_string(imp_mission["descriptionRedTask"])
        self.sortie = self.translation.get_string(imp_mission["sortie"])
        self.pictureFileNameR = imp_mission["pictureFileNameR"]
        self.pictureFileNameB = imp_mission["pictureFileNameB"]
        self.version = imp_mission["version"]
        self.currentKey = imp_mission["currentKey"]
        self.start_time = imp_mission["start_time"]
        self.usedModules = imp_mission["usedModules"]

        # import coalition
        def imp_coalition(coalition, key):
            if key not in coalition:
                return None
            imp_col = coalition[key]
            col = Coalition(key, imp_col["bullseye"])
            for country_idx in imp_col["country"]:
                imp_country = imp_col["country"][country_idx]
                country = Country(imp_country["id"], imp_country["name"])

                if "vehicle" in imp_country:
                    for vgroup_idx in imp_country["vehicle"]["group"]:
                        vgroup = imp_country["vehicle"]["group"][vgroup_idx]
                        vg = VehicleGroup(vgroup["task"], self.translation.get_string(vgroup["name"]), vgroup["start_time"])

                        self._import_point(vg, vgroup)

                        # units
                        for imp_unit_idx in vgroup["units"]:
                            imp_unit = vgroup["units"][imp_unit_idx]
                            unit = Vehicle(id=imp_unit["unitId"], name=self.translation.get_string(imp_unit["name"]))
                            unit.set_position(MapPosition(imp_unit["x"], imp_unit["y"]))
                            unit.heading = imp_unit["heading"]
                            unit.type = imp_unit["type"]
                            unit.skill = imp_unit["skill"]
                            unit.x = imp_unit["x"]
                            unit.y = imp_unit["y"]
                            unit.player_can_drive = imp_unit["playerCanDrive"]
                            unit.transportable = imp_unit["transportable"]
                            vg.add_unit(unit)
                        country.add_vehicle_group(vg)

                if "plane" in imp_country:
                    for pgroup_idx in imp_country["plane"]["group"]:
                        pgroup = imp_country["plane"]["group"][pgroup_idx]
                        plane_group = PlaneGroup(pgroup["task"], self.translation.get_string(pgroup["name"]), pgroup["start_time"])
                        plane_group.frequency = pgroup["frequency"]
                        plane_group.modulation = pgroup["modulation"]
                        plane_group.communication = pgroup["communication"]
                        plane_group.uncontrolled = pgroup["uncontrolled"]

                        self._import_point(plane_group, pgroup)

                        # units
                        for imp_unit_idx in pgroup["units"]:
                            imp_unit = pgroup["units"][imp_unit_idx]
                            plane = Plane(id=imp_unit["unitId"], name=self.translation.get_string(imp_unit["name"]))
                            plane.set_position(MapPosition(imp_unit["x"], imp_unit["y"]))
                            plane.heading = imp_unit["heading"]
                            plane.type = imp_unit["type"]
                            plane.skill = imp_unit["skill"]
                            plane.livery_id = imp_unit["livery_id"]
                            plane.x = imp_unit["x"]
                            plane.y = imp_unit["y"]
                            plane.alt_type = imp_unit["alt_type"]
                            plane.alt = imp_unit["alt"]
                            plane.psi = imp_unit["psi"]
                            plane.speed = imp_unit["speed"]
                            plane.fuel = imp_unit["payload"]["fuel"]
                            plane.gun = imp_unit["payload"]["gun"]
                            plane.flare = imp_unit["payload"]["flare"]
                            plane.chaff = imp_unit["payload"]["chaff"]
                            plane.ammo_type = imp_unit["payload"]["ammo_type"]
                            plane.pylons = imp_unit["payload"]["pylons"]
                            plane_group.add_unit(plane)
                        country.add_plane_group(plane_group)
                col.add_country(country)
            return col
        # blue
        self.coalition["blue"] = imp_coalition(imp_mission["coalition"], "blue")
        self.coalition["red"] = imp_coalition(imp_mission["coalition"], "red")
        neutral_col = imp_coalition(imp_mission["coalition"], "neutral")
        if neutral_col:
            self.coalition["neutral"] = imp_coalition(imp_mission["coalition"], "neutral")

        return True

    def description_text(self):
        return str(self.description_text)

    def set_description_text(self, text):
        self.description_text.set(text)

    def description_bluetask_text(self):
        return str(self.description_bluetask)

    def set_description_bluetask_text(self, text):
        self.description_bluetask.set(text)

    def description_redtask_text(self):
        return str(self.description_redtask)

    def set_description_redtask_text(self, text):
        self.description_redtask.set(text)

    def string(self, s):
        return "not implemented"

    def save(self, filename):
        return False

    def __str__(self):
        m = {}
        m["trig"] = self.trig
        m["result"] = self.result
        m["groundControl"] = self.groundControl
        m["usedModules"] = self.usedModules
        m["resourceCounter"] = self.resourceCounter
        m["triggers"] = self.triggers
        m["weather"] = self.weather.dict()
        m["theatre"] = self.theatre
        m["needModules"] = self.needModules
        m["map"] = {}
        m["descriptionText"] = self.description_text.id()
        m["pictureFileNameR"] = self.pictureFileNameR
        m["pictureFileNameB"] = self.pictureFileNameB
        m["descriptionBlueTask"] = self.description_bluetask.id()
        m["descriptionRedTask"] = self.description_redtask.id()
        m["trigrules"] = {}
        m["coalition"] = {}
        for col in self.coalition.keys():
            m["coalition"][col] = self.coalition[col].dict()
        m["coalitions"] = {}  # generate from coalition
        m["sortie"] = self.sortie.id()
        m["version"] = self.version
        m["goals"] = self.goals
        m["currentKey"] = self.currentKey
        m["start_time"] = self.start_time
        m["forcedOptions"] = self.forcedOptions
        m["failures"] = self.failures

        return lua.dumps(m, "mission", 1)

    def __repr__(self):
        rep = {"base": self.values, "options": self.options, "translation": self.translation}
        return repr(rep)
