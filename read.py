import ephem
from astropy.time import Time
from astropy import units as u
# from exputil import parse_positive_int

def read_tle(filename_tles):
    """
    Read a constellation of satellites from the TLES file.

    :param filename_tles:                    Filename of the TLES (typically /path/to/tles.txt)

    :return: Dictionary: {
                    "n_orbits":             Number of orbits
                    "n_sats_per_orbit":     Satellites per orbit
                    "epoch":                Epoch
                    "satellites":           Dictionary of satellite id to
                                            {"ephem_obj_manual": <obj>, "ephem_obj_direct": <obj>}
              }
    """
    satellites = []
    with open(filename_tles, 'r') as f:
        n_orbits, n_sats_per_orbit = [int(n) for n in f.readline().split()]
        universal_epoch = None
        i = 0
        for tles_line_1 in f:
            tles_line_2 = f.readline()
            tles_line_3 = f.readline()

            # Retrieve name and identifier
            name = tles_line_1
            sid = int(name.split()[1])
            if sid != i:
                raise ValueError("Satellite identifier is not increasing by one each line")
            i += 1

            # Fetch and check the epoch from the TLES data
            # In the TLE, the epoch is given with a Julian data of yyddd.fraction
            # ddd is actually one-based, meaning e.g. 18001 is 1st of January, or 2018-01-01 00:00.
            # As such, to convert it to Astropy Time, we add (ddd - 1) days to it
            # See also: https://www.celestrak.com/columns/v04n03/#FAQ04
            epoch_year = tles_line_2[18:20]
            epoch_day = float(tles_line_2[20:32])
            epoch = Time("20" + epoch_year + "-01-01 00:00:00", scale="tdb") + (epoch_day - 1) * u.day
            if universal_epoch is None:
                universal_epoch = epoch
            if epoch != universal_epoch:
                raise ValueError("The epoch of all TLES must be the same")

            # Finally, store the satellite information
            satellites.append(ephem.readtle(tles_line_1, tles_line_2, tles_line_3))

    return {
        "n_orbits": n_orbits,
        "n_sats_per_orbit": n_sats_per_orbit,
        "epoch": epoch,
        "satellites": satellites
    }

def read_isls(filename_isls, num_satellites):
    """
    Read ISLs file into a list of undirected edges

    :param filename_isls:  Filename of ISLs (typically /path/to/isls.txt)
    :param num_satellites: Number of satellites (to verify indices)

    :return: List of all undirected ISL edges
    """
    isls_list = []
    with open(filename_isls, 'r') as f:
        isls_set = set()
        for line in f:
            line_spl = line.split()
            a = int(line_spl[0])
            b = int(line_spl[1])

            # Verify the input
            if a >= num_satellites:
                raise ValueError("Satellite does not exist: %d" % a)
            if b >= num_satellites:
                raise ValueError("Satellite does not exist: %d" % b)
            if b <= a:
                raise ValueError("The second satellite index must be strictly larger than the first")
            if (a, b) in isls_set:
                raise ValueError("Duplicate ISL: (%d, %d)" % (a, b))
            isls_set.add((a, b))

            # Finally add it to the list
            isls_list.append((a, b))

    return isls_list


def read_ground_stations_extended(filename_ground_stations_extended):
    """
    Reads ground stations from the input file.

    :param filename_ground_stations_extended: Filename of ground stations basic (typically /path/to/ground_stations.txt)

    :return: List of ground stations
    """
    ground_stations_extended = []
    gid = 0
    with open(filename_ground_stations_extended, 'r') as f:
        for line in f:
            split = line.split(',')
            if len(split) != 8:
                raise ValueError("Extended ground station file has 8 columns: " + line)
            if int(split[0]) != gid:
                raise ValueError("Ground station id must increment each line")
            ground_station_basic = {
                "gid": gid,
                "name": split[1],
                "latitude_degrees_str": split[2],
                "longitude_degrees_str": split[3],
                "elevation_m_float": float(split[4]),
                "cartesian_x": float(split[5]),
                "cartesian_y": float(split[6]),
                "cartesian_z": float(split[7]),
            }
            ground_stations_extended.append(ground_station_basic)
            gid += 1
    return ground_stations_extended
