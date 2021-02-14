"""
    Sample data for various test cases
"""
MD_MISSING_METADATA = """
# This is a markdown note with no metadata

Here is some data in it
"""

MD_MISSING_END_TOKEN = """
---
title: this is my title
author: John Doe
created: '2021-02-13T20:45:39.889620-05:00'
id: 20210213204539
--
# This is a markdown note with a missing front-matter end token

Here's the content of this text
"""

MD_CORRUPTED_YAML = """
---
title: Discursive Quantum Semiotics: A treatise on interior positionality
author: Fan C. Professor, Ph.D
created: '2021-02-13T15:55:57.632072-05:00'
id: 20210213155557
---
# This is a note with malformed yaml front-matter

This front matter contains a malformed title which will cause the YAML parser to fail.
"""

MD_BROKEN_TIMESTAMP = """
---
title: "My Dissertation: a lesson on enduring tasks that never end"
author: Jane Doe
created: '2020-02-30T16:02:22.422064-05:00'
id: 20210213160222
---
# This is a note with an invalid timestamp

This front matter contains an impossible timestamp that will cause the datetime parser to fail
"""

MD_BROKEN_TIMESTAMP_2 = """
---
title: "My Dissertation: a lesson on enduring tasks that never end"
author: Jane Doe
created: 3
id: 20210213160222
---
# This is a note with an invalid timestamp

This front matter contains an impossible timestamp that will cause the datetime parser to fail
"""

MD_SAMPLE_NOTE_0 = """
...
title: Note Sample 0
author: Robert Robertson
created: '2021-02-13T16:05:25.245783-05:00'
id: 20210213160525
...
# Sample Note 0

This is some text in the sample note 0
"""

MD_SAMPLE_NOTE_1 = """
...
title: Note Sample 1
author: Alice Alison
created: '2021-02-13T16:06:41.927650-05:00'
id: 20210213160641
...
# Sample Note 1

This is some text in the sample note 1
"""

MD_EXTRA_METADATA = """
...
title: Extra Metadata Example
author: Bob Bobertsmith
created: '2021-02-13T17:29:11.879245-05:00'
id: 20210213172911
tags:
 - synergy
 - upcycle
source: IPhone 19
---
# Extra metadata

This note has extra metadata in it
"""


# These are five completely normal notes with valid attributes
INDEX_FIVE_NORMAL_NOTES = {
   '/home/note-00.md': {'content': "---\nauthor: Eva Evanston\ncreated: 2011-01-24 06:33:36+11:00\nid: '20110124063336'\ntitle: Aliqua ullamcorper dignissim\n---\n# Aliqua ullamcorper dignissim\n\nIaculis nunc sed augue lacus viverra vitae congue cras adipiscing enim eu turpis egestas pretium euismod lacinia at quis risus sed.  Mauris auctor neque vitae tempus quam phasellus vestibulum lorem sed risus sed cras ornare arcu dui vivamus arcu lectus.  Risus commodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque id ornare arcu dui vivamus arcu felis bibendum faucibus a pellentesque sit amet.  Tempus quam phasellus vestibulum lorem sed risus sed cras ornare arcu dui vivamus.\n\n", 'modified': 1295811216},
   '/home/note-01.md': {'content': "---\nauthor: Bob Bobertsmith\ncreated: 2007-01-21 17:29:59+02:00\nid: '20070121172959'\ntitle: In magna etiam\n---\n# In magna etiam\n\nConsectetur adipiscing elit sed do eiusmod tempor incididunt.  Lorem ipsum faucibus et molestie ac feugiat sed lectus vestibulum ac auctor augue mauris augue neque gravida in.\n\nRisus sed cras ornare arcu dui vivamus arcu lectus mauris ultrices eros in cursus turpis massa tincidunt id faucibus nisl tincidunt eget nullam non nisi est non quam lacus suspendisse.\n\nVitae congue cras adipiscing enim eu turpis egestas pretium euismod lacinia at quis risus sed vulputate odio at.  Faucibus interdum posuere lorem placerat vestibulum lectus mauris ultrices eros in cursus.  Arcu lectus mauris ultrices eros in cursus turpis massa tincidunt id faucibus.  Bibendum ut tristique libero enim sed faucibus turpis in eu mi bibendum neque morbi tincidunt augue interdum velit euismod in est ante in.  Proin libero iaculis nunc sed augue lacus viverra vitae congue cras adipiscing enim eu turpis egestas pretium euismod lacinia.\n\n", 'modified': 1169393399},
   '/home/note-02.md': {'content': "---\nauthor: Charles Charleston\ncreated: 2013-05-23 17:54:49-10:00\nid: '20130523175449'\ntitle: Lorem ipsum cursus mattis molestie a iaculis at\n---\n# Lorem ipsum cursus mattis molestie a iaculis at\n\nMauris cursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat vestibulum lectus mauris auctor elit.\n\nTincidunt dui ut aenean pharetra magna ac placerat vestibulum lectus mauris auctor elit sed vulputate mi morbi blandit cursus risus at ultrices mi tempus imperdiet.  Mauris cursus mattis molestie a iaculis at erat neque gravida in fermentum et at quis risus sed vulputate odio tempus egestas sed sed risus vivamus arcu felis bibendum ut tristique.\n\nPellentesque nec nam aliquam sem et tortor amet.  Mauris auctor neque vitae tempus quam phasellus vestibulum lorem sed risus sed cras ornare arcu dui vivamus arcu lectus mauris ultrices eros in cursus turpis massa tincidunt id faucibus.  Auctor neque vitae tempus quam ut consequat semper.  Cursus turpis massa tincidunt dui ut aenean pharetra magna ac.  Consequat semper viverra nam libero justo laoreet nunc vel risus commodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque id ornare arcu dui vivamus.\n\n", 'modified': 1369367689},
   '/home/note-03.md': {'content': "---\nauthor: Alice Allison\ncreated: 2016-10-10 06:12:47-03:00\nid: '20161010061247'\ntitle: Dolor magna eget est lorem\n---\n# Dolor magna eget est lorem\n\nDolore magna aliqua ullamcorper dignissim cras tincidunt lobortis sit amet volutpat consequat mauris auctor neque vitae tempus quam phasellus vestibulum lorem sed risus sed cras ornare.  Varius tincidunt id aliquet risus feugiat in.\n\nLacus viverra vitae congue cras adipiscing enim eu turpis egestas pretium euismod lacinia at quis risus sed vulputate odio at risus.  Orci porta non pulvinar neque laoreet suspendisse iaculis at erat pellentesque adipiscing commodo elit at imperdiet dui.  Feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue lacus viverra vitae congue cras adipiscing enim.  Placerat vestibulum lectus mauris ultrices eros in.\n\nFaucibus nisl tincidunt eget nullam et ligula ullamcorper malesuada proin in nibh mauris cursus mattis molestie a iaculis ultrices eros in cursus.  Lectus nulla at volutpat pellentesque nec nam.  Eu lobortis elementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue lacus viverra vitae congue cras.  Quis lectus nulla at volutpat.\n\n", 'modified': 1476090767},
   '/home/note-04.md': {'content': "---\nauthor: Eva Evanston\ncreated: 2002-07-26 14:44:34+10:00\nid: '20020726144434'\ntitle: Tempor incididunt ut labore et dolore magna aliqua\n---\n# Tempor incididunt ut labore et dolore magna aliqua\n\nCommodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque id ornare arcu dui vivamus arcu felis bibendum faucibus a pellentesque sit amet porttitor diam phasellus vestibulum.  Enim sed faucibus turpis in eu mi bibendum neque morbi tincidunt augue interdum velit euismod in.  Faucibus nisl tincidunt eget nullam et ligula ullamcorper malesuada proin in nibh mauris cursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean.  Ante in nibh quisque non tellus.  Diam in est ante in nibh quisque non tellus orci ac auctor mi quis hendrerit dolor.\n\nAc auctor augue mauris augue neque gravida in magna.  Cras adipiscing enim eu turpis egestas pretium euismod lacinia at quis risus sed vulputate.\n\n", 'modified': 1027658674}
}

# This index contains three normal notes, and one note missing each critical attribute (the missing ID note also is
# missing the creation timestamp)
INDEX_WITH_MISSING_ATTRS = {
   '/alpha/note-00.md': {'content': "---\nauthor: Alice Allison\ncreated: 2024-01-02 08:01:35+02:00\nid: '20240102080135'\ntitle: Auctor neque vitae tempus quam phasellus vestibulum lorem\n---\n# Auctor neque vitae tempus quam phasellus vestibulum lorem\n\nMolestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis.  Et tortor amet nisl purus in mollis ullamcorper malesuada proin libero nunc consequat interdum varius tincidunt id aliquet risus feugiat in.\n\nPurus in mollis ullamcorper malesuada proin libero nunc consequat interdum varius tincidunt id aliquet risus feugiat in ante enim neque volutpat ac tincidunt vitae.  Quis hendrerit dolor magna eget est lorem ipsum faucibus et molestie ac feugiat sed lectus.\n\nCommodo elit at imperdiet dui lacus sed turpis tincidunt id aliquet risus libero.  Faucibus interdum posuere lorem placerat vestibulum lectus mauris ultrices eros in cursus turpis massa nullam ac tortor vitae.  Ante in nibh mauris cursus mattis molestie tincidunt vitae semper quis lectus nulla at.  Dolore magna aliqua ullamcorper dignissim cras tincidunt lobortis sit amet volutpat consequat.\n\n", 'modified': 1704175295},
   '/alpha/note-01.md': {'content': "---\nauthor: Bob Bobertsmith\ncreated: 1999-09-07 01:21:14+02:00\nid: '19990907012114'\ntitle: Lorem sed risus sed cras ornare\n---\n# Lorem sed risus sed cras ornare\n\nMolestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue lacus.  Enim in nibh mauris cursus mattis molestie a iaculis at erat neque gravida in fermentum et at quis risus sed vulputate odio tempus egestas.\n\nTempor orci eu lobortis elementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue lacus viverra vitae congue cras adipiscing.  Volutpat ac tincidunt vitae semper quis lectus at consectetur lorem donec massa sapien faucibus.\n\nImperdiet dui lacus sed turpis tincidunt id aliquet risus libero id faucibus nisl tincidunt eget nullam et ligula.  Risus sed vulputate odio tempus egestas sed sed risus vivamus.\n\n", 'modified': 936660074},
   '/alpha/note-02.md': {'content': "---\nauthor: Eva Evanston\ncreated: 2000-10-01 03:31:44+03:00\nid: '20001001033144'\ntitle: Elementum nibh tellus molestie massa sapien\n---\n# Elementum nibh tellus molestie massa sapien\n\nAdipiscing commodo elit at imperdiet dui lacus sed turpis tincidunt id aliquet risus libero id faucibus nisl tincidunt eget nullam et ligula ullamcorper malesuada proin in nibh.  Adipiscing commodo elit at imperdiet dui lacus sed turpis tincidunt id aliquet risus.  Nunc consequat interdum varius tincidunt id aliquet risus feugiat in ante enim neque volutpat ac.  Malesuada proin in nibh mauris cursus mattis molestie a.  Semper auctor neque vitae tempus quam ut.\n\n", 'modified': 970360304},
   '/alpha/missing-author.md': {'content': "---\nauthor: null\ncreated: 2013-09-23 09:20:50-07:00\nid: '20130923092050'\ntitle: At in tellus lectus arcu bibendum at varius\n---\n# At in tellus lectus arcu bibendum at varius\n\nMassa nullam ac tortor vitae purus faucibus quis hendrerit dolor magna eget.  Felis bibendum ut tristique libero enim sed faucibus turpis in eu mi.  Cursus mattis molestie tincidunt vitae semper quis lectus nulla at volutpat pellentesque nec nam aliquam sem et tortor amet nisl purus in mollis ullamcorper malesuada proin libero nunc.  Hendrerit dolor magna eget est lorem ipsum cursus mattis molestie a iaculis at erat pellentesque pellentesque elit eget gravida cum vel orci.  Suspendisse faucibus interdum posuere lorem placerat.\n\n", 'modified': 1379953250},
   '/alpha/missing-created.md': {'content': '---\nauthor: Dave Davidson\ncreated: null\nid: null\ntitle: Feugiat in ante enim neque volutpat ac\n---\n# Feugiat in ante enim neque volutpat ac\n\nConsequat semper viverra nam libero justo laoreet nunc vel risus commodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque id ornare arcu dui vivamus arcu.  Donec enim in nibh mauris.\n\n', 'modified': 685551690},
   '/alpha/missing-id.md': {'content': '---\nauthor: Fiona Fiorella\ncreated: 2004-09-17 03:22:20+03:00\nid: null\ntitle: A iaculis at erat\n---\n# A iaculis at erat\n\nAliquet risus libero id faucibus nisl tincidunt eget nullam et ligula ullamcorper malesuada proin in.  Vestibulum ac auctor augue mauris augue neque gravida in magna etiam tempor orci eu lobortis elementum nibh tellus molestie massa sapien.\n\n', 'modified': 1095380540},
   '/alpha/missing-title.md': {'content': "---\nauthor: Eva Evanston\ncreated: 2008-10-14 00:51:49+02:00\nid: '20081014005149'\ntitle: null\n---\n# Euismod in est ante in\n\nRisus sed vulputate odio at risus viverra adipiscing at in tellus lectus arcu bibendum at varius vel pharetra vel amet.  Dui lacus sed turpis tincidunt.  Mauris cursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat vestibulum lectus mauris.  Phasellus vestibulum lorem sed risus sed cras ornare arcu dui vivamus arcu lectus.  Tincidunt id aliquet risus feugiat.\n\nLigula ullamcorper malesuada proin in nibh mauris cursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat vestibulum.\n\nOdio tempus egestas sed sed risus vivamus.  Proin libero nunc consequat interdum varius tincidunt id aliquet risus feugiat in ante enim neque.  Diam phasellus vestibulum lorem sed risus ultricies tristique nulla odio aenean sed adipiscing diam in est ante in nibh quisque non tellus orci ac.\n\n", 'modified': 1223938309},
}