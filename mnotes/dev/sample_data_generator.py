from typing import Dict, List

import yaml
import io
import string
import random
from mnotes.environment import ID_TIME_FORMAT
from datetime import datetime as DateTime
from dateutil import tz

AUTHORS = ["Alice Allison", "Bob Bobertsmith", "Charles Charleston", "Dave Davidson", "Eva Evanston",
           "Fiona Fiorella"]

ALL_TIME_ZONES = ['Africa/Abidjan', 'Africa/Accra', 'Africa/Addis_Ababa', 'Africa/Algiers', 'Africa/Asmara',
                  'Africa/Asmera', 'Africa/Bamako', 'Africa/Bangui', 'Africa/Banjul', 'Africa/Bissau',
                  'Africa/Blantyre', 'Africa/Brazzaville', 'Africa/Bujumbura', 'Africa/Cairo', 'Africa/Casablanca',
                  'Africa/Ceuta', 'Africa/Conakry', 'Africa/Dakar', 'Africa/Dar_es_Salaam', 'Africa/Djibouti',
                  'Africa/Douala', 'Africa/El_Aaiun', 'Africa/Freetown', 'Africa/Gaborone', 'Africa/Harare',
                  'Africa/Johannesburg', 'Africa/Juba', 'Africa/Kampala', 'Africa/Khartoum', 'Africa/Kigali',
                  'Africa/Kinshasa', 'Africa/Lagos', 'Africa/Libreville', 'Africa/Lome', 'Africa/Luanda',
                  'Africa/Lubumbashi', 'Africa/Lusaka', 'Africa/Malabo', 'Africa/Maputo', 'Africa/Maseru',
                  'Africa/Mbabane', 'Africa/Mogadishu', 'Africa/Monrovia', 'Africa/Nairobi', 'Africa/Ndjamena',
                  'Africa/Niamey', 'Africa/Nouakchott', 'Africa/Ouagadougou', 'Africa/Porto-Novo', 'Africa/Sao_Tome',
                  'Africa/Timbuktu', 'Africa/Tripoli', 'Africa/Tunis', 'Africa/Windhoek', 'America/Adak',
                  'America/Anchorage', 'America/Anguilla', 'America/Antigua', 'America/Araguaina',
                  'America/Argentina/Buenos_Aires', 'America/Argentina/Catamarca', 'America/Argentina/ComodRivadavia',
                  'America/Argentina/Cordoba', 'America/Argentina/Jujuy', 'America/Argentina/La_Rioja',
                  'America/Argentina/Mendoza', 'America/Argentina/Rio_Gallegos', 'America/Argentina/Salta',
                  'America/Argentina/San_Juan', 'America/Argentina/San_Luis', 'America/Argentina/Tucuman',
                  'America/Argentina/Ushuaia', 'America/Aruba', 'America/Asuncion', 'America/Atikokan', 'America/Atka',
                  'America/Bahia', 'America/Bahia_Banderas', 'America/Barbados', 'America/Belem', 'America/Belize',
                  'America/Blanc-Sablon', 'America/Boa_Vista', 'America/Bogota', 'America/Boise',
                  'America/Buenos_Aires', 'America/Cambridge_Bay', 'America/Campo_Grande', 'America/Cancun',
                  'America/Caracas', 'America/Catamarca', 'America/Cayenne', 'America/Cayman', 'America/Chicago',
                  'America/Chihuahua', 'America/Coral_Harbour', 'America/Cordoba', 'America/Costa_Rica',
                  'America/Creston', 'America/Cuiaba', 'America/Curacao', 'America/Danmarkshavn', 'America/Dawson',
                  'America/Dawson_Creek', 'America/Denver', 'America/Detroit', 'America/Dominica', 'America/Edmonton',
                  'America/Eirunepe', 'America/El_Salvador', 'America/Ensenada', 'America/Fort_Nelson',
                  'America/Fort_Wayne', 'America/Fortaleza', 'America/Glace_Bay', 'America/Godthab',
                  'America/Goose_Bay', 'America/Grand_Turk', 'America/Grenada', 'America/Guadeloupe',
                  'America/Guatemala', 'America/Guayaquil', 'America/Guyana', 'America/Halifax', 'America/Havana',
                  'America/Hermosillo', 'America/Indiana/Indianapolis', 'America/Indiana/Knox',
                  'America/Indiana/Marengo', 'America/Indiana/Petersburg', 'America/Indiana/Tell_City',
                  'America/Indiana/Vevay', 'America/Indiana/Vincennes', 'America/Indiana/Winamac',
                  'America/Indianapolis', 'America/Inuvik', 'America/Iqaluit', 'America/Jamaica', 'America/Jujuy',
                  'America/Juneau', 'America/Kentucky/Louisville', 'America/Kentucky/Monticello', 'America/Knox_IN',
                  'America/Kralendijk', 'America/La_Paz', 'America/Lima', 'America/Los_Angeles', 'America/Louisville',
                  'America/Lower_Princes', 'America/Maceio', 'America/Managua', 'America/Manaus', 'America/Marigot',
                  'America/Martinique', 'America/Matamoros', 'America/Mazatlan', 'America/Mendoza', 'America/Menominee',
                  'America/Merida', 'America/Metlakatla', 'America/Mexico_City', 'America/Miquelon', 'America/Moncton',
                  'America/Monterrey', 'America/Montevideo', 'America/Montreal', 'America/Montserrat', 'America/Nassau',
                  'America/New_York', 'America/Nipigon', 'America/Nome', 'America/Noronha',
                  'America/North_Dakota/Beulah', 'America/North_Dakota/Center', 'America/North_Dakota/New_Salem',
                  'America/Nuuk', 'America/Ojinaga', 'America/Panama', 'America/Pangnirtung', 'America/Paramaribo',
                  'America/Phoenix', 'America/Port-au-Prince', 'America/Port_of_Spain', 'America/Porto_Acre',
                  'America/Porto_Velho', 'America/Puerto_Rico', 'America/Punta_Arenas', 'America/Rainy_River',
                  'America/Rankin_Inlet', 'America/Recife', 'America/Regina', 'America/Resolute', 'America/Rio_Branco',
                  'America/Rosario', 'America/Santa_Isabel', 'America/Santarem', 'America/Santiago',
                  'America/Santo_Domingo', 'America/Sao_Paulo', 'America/Scoresbysund', 'America/Shiprock',
                  'America/Sitka', 'America/St_Barthelemy', 'America/St_Johns', 'America/St_Kitts', 'America/St_Lucia',
                  'America/St_Thomas', 'America/St_Vincent', 'America/Swift_Current', 'America/Tegucigalpa',
                  'America/Thule', 'America/Thunder_Bay', 'America/Tijuana', 'America/Toronto', 'America/Tortola',
                  'America/Vancouver', 'America/Virgin', 'America/Whitehorse', 'America/Winnipeg', 'America/Yakutat',
                  'America/Yellowknife', 'Antarctica/Casey', 'Antarctica/Davis', 'Antarctica/DumontDUrville',
                  'Antarctica/Macquarie', 'Antarctica/Mawson', 'Antarctica/McMurdo', 'Antarctica/Palmer',
                  'Antarctica/Rothera', 'Antarctica/South_Pole', 'Antarctica/Syowa', 'Antarctica/Troll',
                  'Antarctica/Vostok', 'Arctic/Longyearbyen', 'Asia/Aden', 'Asia/Almaty', 'Asia/Amman', 'Asia/Anadyr',
                  'Asia/Aqtau', 'Asia/Aqtobe', 'Asia/Ashgabat', 'Asia/Ashkhabad', 'Asia/Atyrau', 'Asia/Baghdad',
                  'Asia/Bahrain', 'Asia/Baku', 'Asia/Bangkok', 'Asia/Barnaul', 'Asia/Beirut', 'Asia/Bishkek',
                  'Asia/Brunei', 'Asia/Calcutta', 'Asia/Chita', 'Asia/Choibalsan', 'Asia/Chongqing', 'Asia/Chungking',
                  'Asia/Colombo', 'Asia/Dacca', 'Asia/Damascus', 'Asia/Dhaka', 'Asia/Dili', 'Asia/Dubai',
                  'Asia/Dushanbe', 'Asia/Famagusta', 'Asia/Gaza', 'Asia/Harbin', 'Asia/Hebron', 'Asia/Ho_Chi_Minh',
                  'Asia/Hong_Kong', 'Asia/Hovd', 'Asia/Irkutsk', 'Asia/Istanbul', 'Asia/Jakarta', 'Asia/Jayapura',
                  'Asia/Jerusalem', 'Asia/Kabul', 'Asia/Kamchatka', 'Asia/Karachi', 'Asia/Kashgar', 'Asia/Kathmandu',
                  'Asia/Katmandu', 'Asia/Khandyga', 'Asia/Kolkata', 'Asia/Krasnoyarsk', 'Asia/Kuala_Lumpur',
                  'Asia/Kuching', 'Asia/Kuwait', 'Asia/Macao', 'Asia/Macau', 'Asia/Magadan', 'Asia/Makassar',
                  'Asia/Manila', 'Asia/Muscat', 'Asia/Nicosia', 'Asia/Novokuznetsk', 'Asia/Novosibirsk', 'Asia/Omsk',
                  'Asia/Oral', 'Asia/Phnom_Penh', 'Asia/Pontianak', 'Asia/Pyongyang', 'Asia/Qatar', 'Asia/Qostanay',
                  'Asia/Qyzylorda', 'Asia/Rangoon', 'Asia/Riyadh', 'Asia/Saigon', 'Asia/Sakhalin', 'Asia/Samarkand',
                  'Asia/Seoul', 'Asia/Shanghai', 'Asia/Singapore', 'Asia/Srednekolymsk', 'Asia/Taipei', 'Asia/Tashkent',
                  'Asia/Tbilisi', 'Asia/Tehran', 'Asia/Tel_Aviv', 'Asia/Thimbu', 'Asia/Thimphu', 'Asia/Tokyo',
                  'Asia/Tomsk', 'Asia/Ujung_Pandang', 'Asia/Ulaanbaatar', 'Asia/Ulan_Bator', 'Asia/Urumqi',
                  'Asia/Ust-Nera', 'Asia/Vientiane', 'Asia/Vladivostok', 'Asia/Yakutsk', 'Asia/Yangon',
                  'Asia/Yekaterinburg', 'Asia/Yerevan', 'Atlantic/Azores', 'Atlantic/Bermuda', 'Atlantic/Canary',
                  'Atlantic/Cape_Verde', 'Atlantic/Faeroe', 'Atlantic/Faroe', 'Atlantic/Jan_Mayen', 'Atlantic/Madeira',
                  'Atlantic/Reykjavik', 'Atlantic/South_Georgia', 'Atlantic/St_Helena', 'Atlantic/Stanley',
                  'Australia/ACT', 'Australia/Adelaide', 'Australia/Brisbane', 'Australia/Broken_Hill',
                  'Australia/Canberra', 'Australia/Currie', 'Australia/Darwin', 'Australia/Eucla', 'Australia/Hobart',
                  'Australia/LHI', 'Australia/Lindeman', 'Australia/Lord_Howe', 'Australia/Melbourne', 'Australia/NSW',
                  'Australia/North', 'Australia/Perth', 'Australia/Queensland', 'Australia/South', 'Australia/Sydney',
                  'Australia/Tasmania', 'Australia/Victoria', 'Australia/West', 'Australia/Yancowinna', 'Brazil/Acre',
                  'Brazil/DeNoronha', 'Brazil/East', 'Brazil/West', 'CET', 'CST6CDT', 'Canada/Atlantic',
                  'Canada/Central', 'Canada/Eastern', 'Canada/Mountain', 'Canada/Newfoundland', 'Canada/Pacific',
                  'Canada/Saskatchewan', 'Canada/Yukon', 'Chile/Continental', 'Chile/EasterIsland', 'Cuba', 'EET',
                  'EST', 'EST5EDT', 'Egypt', 'Eire', 'Etc/GMT', 'Etc/GMT+0', 'Etc/GMT+1', 'Etc/GMT+10', 'Etc/GMT+11',
                  'Etc/GMT+12', 'Etc/GMT+2', 'Etc/GMT+3', 'Etc/GMT+4', 'Etc/GMT+5', 'Etc/GMT+6', 'Etc/GMT+7',
                  'Etc/GMT+8', 'Etc/GMT+9', 'Etc/GMT-0', 'Etc/GMT-1', 'Etc/GMT-10', 'Etc/GMT-11', 'Etc/GMT-12',
                  'Etc/GMT-13', 'Etc/GMT-14', 'Etc/GMT-2', 'Etc/GMT-3', 'Etc/GMT-4', 'Etc/GMT-5', 'Etc/GMT-6',
                  'Etc/GMT-7', 'Etc/GMT-8', 'Etc/GMT-9', 'Etc/GMT0', 'Etc/Greenwich', 'Etc/UCT', 'Etc/UTC',
                  'Etc/Universal', 'Etc/Zulu', 'Europe/Amsterdam', 'Europe/Andorra', 'Europe/Astrakhan',
                  'Europe/Athens', 'Europe/Belfast', 'Europe/Belgrade', 'Europe/Berlin', 'Europe/Bratislava',
                  'Europe/Brussels', 'Europe/Bucharest', 'Europe/Budapest', 'Europe/Busingen', 'Europe/Chisinau',
                  'Europe/Copenhagen', 'Europe/Dublin', 'Europe/Gibraltar', 'Europe/Guernsey', 'Europe/Helsinki',
                  'Europe/Isle_of_Man', 'Europe/Istanbul', 'Europe/Jersey', 'Europe/Kaliningrad', 'Europe/Kiev',
                  'Europe/Kirov', 'Europe/Lisbon', 'Europe/Ljubljana', 'Europe/London', 'Europe/Luxembourg',
                  'Europe/Madrid', 'Europe/Malta', 'Europe/Mariehamn', 'Europe/Minsk', 'Europe/Monaco', 'Europe/Moscow',
                  'Europe/Nicosia', 'Europe/Oslo', 'Europe/Paris', 'Europe/Podgorica', 'Europe/Prague', 'Europe/Riga',
                  'Europe/Rome', 'Europe/Samara', 'Europe/San_Marino', 'Europe/Sarajevo', 'Europe/Saratov',
                  'Europe/Simferopol', 'Europe/Skopje', 'Europe/Sofia', 'Europe/Stockholm', 'Europe/Tallinn',
                  'Europe/Tirane', 'Europe/Tiraspol', 'Europe/Ulyanovsk', 'Europe/Uzhgorod', 'Europe/Vaduz',
                  'Europe/Vatican', 'Europe/Vienna', 'Europe/Vilnius', 'Europe/Volgograd', 'Europe/Warsaw',
                  'Europe/Zagreb', 'Europe/Zaporozhye', 'Europe/Zurich', 'GB', 'GB-Eire', 'GMT', 'GMT+0', 'GMT-0',
                  'GMT0', 'Greenwich', 'HST', 'Hongkong', 'Iceland', 'Indian/Antananarivo', 'Indian/Chagos',
                  'Indian/Christmas', 'Indian/Cocos', 'Indian/Comoro', 'Indian/Kerguelen', 'Indian/Mahe',
                  'Indian/Maldives', 'Indian/Mauritius', 'Indian/Mayotte', 'Indian/Reunion', 'Iran', 'Israel',
                  'Jamaica', 'Japan', 'Kwajalein', 'Libya', 'MET', 'MST', 'MST7MDT', 'Mexico/BajaNorte',
                  'Mexico/BajaSur', 'Mexico/General', 'NZ', 'NZ-CHAT', 'Navajo', 'PRC', 'PST8PDT', 'Pacific/Apia',
                  'Pacific/Auckland', 'Pacific/Bougainville', 'Pacific/Chatham', 'Pacific/Chuuk', 'Pacific/Easter',
                  'Pacific/Efate', 'Pacific/Enderbury', 'Pacific/Fakaofo', 'Pacific/Fiji', 'Pacific/Funafuti',
                  'Pacific/Galapagos', 'Pacific/Gambier', 'Pacific/Guadalcanal', 'Pacific/Guam', 'Pacific/Honolulu',
                  'Pacific/Johnston', 'Pacific/Kiritimati', 'Pacific/Kosrae', 'Pacific/Kwajalein', 'Pacific/Majuro',
                  'Pacific/Marquesas', 'Pacific/Midway', 'Pacific/Nauru', 'Pacific/Niue', 'Pacific/Norfolk',
                  'Pacific/Noumea', 'Pacific/Pago_Pago', 'Pacific/Palau', 'Pacific/Pitcairn', 'Pacific/Pohnpei',
                  'Pacific/Ponape', 'Pacific/Port_Moresby', 'Pacific/Rarotonga', 'Pacific/Saipan', 'Pacific/Samoa',
                  'Pacific/Tahiti', 'Pacific/Tarawa', 'Pacific/Tongatapu', 'Pacific/Truk', 'Pacific/Wake',
                  'Pacific/Wallis', 'Pacific/Yap', 'Poland', 'Portugal', 'ROC', 'ROK', 'Singapore', 'Turkey', 'UCT',
                  'US/Alaska', 'US/Aleutian', 'US/Arizona', 'US/Central', 'US/East-Indiana', 'US/Eastern', 'US/Hawaii',
                  'US/Indiana-Starke', 'US/Michigan', 'US/Mountain', 'US/Pacific', 'US/Samoa', 'UTC', 'Universal',
                  'W-SU', 'WET', 'Zulu']

LOREM_IPSUM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ullamcorper dignissim cras tincidunt lobortis. Sit amet volutpat consequat mauris. Auctor neque vitae tempus quam. Phasellus vestibulum lorem sed risus. Sed cras ornare arcu dui vivamus arcu. Lectus mauris ultrices eros in cursus turpis massa tincidunt. Id faucibus nisl tincidunt eget nullam non nisi est. Non quam lacus suspendisse faucibus interdum posuere lorem. Placerat vestibulum lectus mauris ultrices eros in cursus turpis massa. Nullam ac tortor vitae purus faucibus.
Quis hendrerit dolor magna eget est lorem ipsum. Cursus mattis molestie a iaculis at erat pellentesque. Pellentesque elit eget gravida cum. Vel orci porta non pulvinar neque laoreet suspendisse. Iaculis at erat pellentesque adipiscing commodo elit at imperdiet dui. Lacus sed turpis tincidunt id aliquet risus. Libero id faucibus nisl tincidunt eget nullam. Et ligula ullamcorper malesuada proin. In nibh mauris cursus mattis molestie a iaculis. Ultrices eros in cursus turpis massa tincidunt dui ut.
Aenean pharetra magna ac placerat vestibulum lectus mauris. Auctor elit sed vulputate mi. Morbi blandit cursus risus at ultrices mi tempus imperdiet nulla. A cras semper auctor neque vitae tempus quam. Ut consequat semper viverra nam libero justo laoreet. Nunc vel risus commodo viverra maecenas accumsan lacus vel facilisis. Quis varius quam quisque id. Ornare arcu dui vivamus arcu felis bibendum. Faucibus a pellentesque sit amet porttitor. Diam phasellus vestibulum lorem sed risus ultricies tristique nulla.
Odio aenean sed adipiscing diam. In est ante in nibh. Quisque non tellus orci ac auctor. Mi quis hendrerit dolor magna eget est lorem ipsum. Faucibus et molestie ac feugiat sed lectus vestibulum. Ac auctor augue mauris augue neque gravida in. Magna etiam tempor orci eu lobortis elementum nibh tellus molestie. Massa sapien faucibus et molestie ac feugiat. Ligula ullamcorper malesuada proin libero. Iaculis nunc sed augue lacus viverra vitae congue.
Cras adipiscing enim eu turpis egestas pretium. Euismod lacinia at quis risus sed vulputate odio. At risus viverra adipiscing at in tellus. Lectus arcu bibendum at varius vel pharetra vel. Amet dictum sit amet justo donec enim. In nibh mauris cursus mattis molestie a iaculis at erat. Neque gravida in fermentum et. At quis risus sed vulputate odio. Tempus egestas sed sed risus. Vivamus arcu felis bibendum ut tristique. Libero enim sed faucibus turpis in eu mi bibendum neque. Morbi tincidunt augue interdum velit euismod in. Est ante in nibh mauris cursus mattis molestie. Tincidunt vitae semper quis lectus nulla at volutpat. Pellentesque nec nam aliquam sem et tortor. Amet nisl purus in mollis. Ullamcorper malesuada proin libero nunc consequat interdum varius. Tincidunt id aliquet risus feugiat in ante. Enim neque volutpat ac tincidunt vitae semper quis lectus. At consectetur lorem donec massa sapien faucibus et molestie."""

ALL_WORDS = [word.lower().strip(string.punctuation) for word in LOREM_IPSUM.split()]


def get_random_words(count: int) -> str:
    position = random.randint(0, len(ALL_WORDS) - count - 1)
    return " ".join(ALL_WORDS[position:position + count])


def get_random_sentence() -> str:
    sentence = get_random_words(random.randint(5, 30))
    return sentence[0].upper() + sentence[1:] + "."


def get_random_paragraph() -> str:
    return "  ".join(get_random_sentence() for i in range(random.randint(1, 5)))


def random_note() -> Dict:
    """ Creates a dictionary representing a valid, random note with an author, timestamp, title, ID, and text. Can be
    rendered to text using the render_note(...) function. """
    local_tz = tz.gettz(random.choice(ALL_TIME_ZONES))
    start = int(DateTime(1990, 1, 1).timestamp())
    end = int(DateTime(2025, 1, 1).timestamp())
    created = DateTime.fromtimestamp(random.randint(start, end), tz=local_tz)
    title = get_random_words(random.randint(3, 8))
    title = title[0].upper() + title[1:]
    data = {
        "title": title,
        "author": random.choice(AUTHORS),
        "created": created,
        "id": created.strftime(ID_TIME_FORMAT)
    }

    with io.StringIO() as output:
        output.write(f"# {title}\n\n")
        for i in range(random.randint(1, 3)):
            output.write(f"{get_random_paragraph()}\n\n")
        data['content'] = output.getvalue()
    return data


def conflicting_ids(count: int) -> List[Dict]:
    """ Produces *count* notes which have conflicting IDs """
    notes = [random_note() for i in range(count)]
    for note in notes[1:]:
        note["created"] = notes[0]["created"]
        note["id"] = notes[0]["id"]
    return notes


def _remove_attribute(note_dict: Dict, attribute: str) -> Dict:
    """ Create a copy of the note where a single attribute is removed """
    d = dict(note_dict)
    d[attribute] = None
    return d


def remove_title(note_dict: Dict) -> Dict:
    """ Create a copy of the note where the title is removed """
    return _remove_attribute(note_dict, "title")


def remove_author(note_dict: Dict) -> Dict:
    """ Create a copy of the note where the author is removed """
    return _remove_attribute(note_dict, "author")


def remove_created(note_dict: Dict) -> Dict:
    """ Create a copy of the note where the created timestamp is removed """
    return _remove_attribute(note_dict, "created")


def remove_id(note_dict: Dict) -> Dict:
    """ Create a copy of the note where the id is removed """
    return _remove_attribute(note_dict, "id")


def render_note(data: Dict) -> str:
    meta = dict(data)
    del meta['content']
    with io.StringIO() as output:
        output.write("---\n")
        yaml.dump(meta, output)
        output.write("---\n")
        output.write(data['content'])
        return output.getvalue()


if __name__ == '__main__':

    backing = {}
    # for folder in ["bravo", "charlie", "delta"]:
    #     for i in range(3):
    #         note = random_note()
    #         created: DateTime = note['created']
    #         backing[f"/{folder}/note-{i:02d}.md"] = {
    #             "content": render_note(note),
    #             "modified": int(created.timestamp())
    #         }
    #
    # conflicts = conflicting_ids(4)
    # paths = ["/bravo/conflict-00.md", "/bravo/conflict-01.md", "/charlie/conflict.md", "/delta/conflict.md"]
    # for path, note in zip(paths, conflicts):
    #     backing[path] = {
    #         "content": render_note(note),
    #         "modified": int(note['created'].timestamp())
    #     }
    #
    for i in range(3):
        note = random_note()
        created: DateTime = note['created']
        note = remove_id(note)

        backing[f"/echo/note-{i:02d}.md"] = {
            "content": render_note(note),
            "modified": int(created.timestamp())
        }

    print("DATA_SET_NAME = {")
    for k, v in backing.items():
        print(f"'{k}': {v},")
    print("}")
