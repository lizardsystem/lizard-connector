
def create(name, location, supplier_code, parameter_referenced_unit=None,
           value_type=1):
    return {

    }
    # name (string) – name of timeseries
    # location (object) – location object or location uuid
    # supplier_code (string) – code of supplier, unique within supplier
    # access_modifier (integer) – one of 0: public, 100: common, 200: private, 300: hidden or 9999: deleted.
    # value_type (integer) – one of 0: integer, 1: float, 4: text, 5: image, 8: movie, 10: file, 12: float array
    # supplier (object) – supplier object or supplier username or null optional
    # parameter_referenced_unit (object) – optional parameter_referenced_unit object or parameter_referenced_unit code
    # device (string) – device type optional
    # description (string) – description optional
    # threshold_min_soft (float) – min soft threshold optional
    # threshold_min_hard (float) – min hard threshold optional
    # threshold_max_soft (float) – max soft threshold optional
    # threshold_max_hard (float) – max hard threshold optional