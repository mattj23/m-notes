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

MD_SAMPLE_WITH_LINKS_0 = """
...
title: Linked Note Sample 0
author: Gary Garrison
backlink: true
created: '2021-02-13T16:06:25.245783-05:00'
id: 20210213160625
...
# Sample Linked Note 0

This is some text in the sample linked note 0

And here is a link to another note [[20210213160641]]

And another link [[surrounded20210213172911with-some-stuff]] to a different note
"""

MD_SAMPLE_MNOTE_SECTION = """
...
title: Note Sample With M-Note Section
author: Harry Harrison
created: '2020-02-13T16:06:41.927650-05:00'
id: 20200213160641
...
# Note Sample that has M-Note Magic Section

This is some text in the sample note 1
---
# M-Note References

this is some data here and 
here's some more
[[20200213160641]]
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

# This mock filesystem contains three normal notes, and one note missing each critical attribute (the missing ID note
# also is missing the creation timestamp)
INDEX_WITH_MISSING_ATTRS = {
   '/alpha/note-00.md': {'content': "---\nauthor: Alice Allison\ncreated: 2024-01-02 08:01:35+02:00\nid: '20240102080135'\ntitle: Auctor neque vitae tempus quam phasellus vestibulum lorem\n---\n# Auctor neque vitae tempus quam phasellus vestibulum lorem\n\nMolestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis.  Et tortor amet nisl purus in mollis ullamcorper malesuada proin libero nunc consequat interdum varius tincidunt id aliquet risus feugiat in.\n\nPurus in mollis ullamcorper malesuada proin libero nunc consequat interdum varius tincidunt id aliquet risus feugiat in ante enim neque volutpat ac tincidunt vitae.  Quis hendrerit dolor magna eget est lorem ipsum faucibus et molestie ac feugiat sed lectus.\n\nCommodo elit at imperdiet dui lacus sed turpis tincidunt id aliquet risus libero.  Faucibus interdum posuere lorem placerat vestibulum lectus mauris ultrices eros in cursus turpis massa nullam ac tortor vitae.  Ante in nibh mauris cursus mattis molestie tincidunt vitae semper quis lectus nulla at.  Dolore magna aliqua ullamcorper dignissim cras tincidunt lobortis sit amet volutpat consequat.\n\n", 'modified': 1704175295},
   '/alpha/note-01.md': {'content': "---\nauthor: Bob Bobertsmith\ncreated: 1999-09-07 01:21:14+02:00\nid: '19990907012114'\ntitle: Lorem sed risus sed cras ornare\n---\n# Lorem sed risus sed cras ornare\n\nMolestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue lacus.  Enim in nibh mauris cursus mattis molestie a iaculis at erat neque gravida in fermentum et at quis risus sed vulputate odio tempus egestas.\n\nTempor orci eu lobortis elementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue lacus viverra vitae congue cras adipiscing.  Volutpat ac tincidunt vitae semper quis lectus at consectetur lorem donec massa sapien faucibus.\n\nImperdiet dui lacus sed turpis tincidunt id aliquet risus libero id faucibus nisl tincidunt eget nullam et ligula.  Risus sed vulputate odio tempus egestas sed sed risus vivamus.\n\n", 'modified': 936660074},
   '/alpha/note-02.md': {'content': "---\nauthor: Eva Evanston\ncreated: 2000-10-01 03:31:44+03:00\nid: '20001001033144'\ntitle: Elementum nibh tellus molestie massa sapien\n---\n# Elementum nibh tellus molestie massa sapien\n\nAdipiscing commodo elit at imperdiet dui lacus sed turpis tincidunt id aliquet risus libero id faucibus nisl tincidunt eget nullam et ligula ullamcorper malesuada proin in nibh.  Adipiscing commodo elit at imperdiet dui lacus sed turpis tincidunt id aliquet risus.  Nunc consequat interdum varius tincidunt id aliquet risus feugiat in ante enim neque volutpat ac.  Malesuada proin in nibh mauris cursus mattis molestie a.  Semper auctor neque vitae tempus quam ut.\n\n", 'modified': 970360304},
   '/alpha/missing-author.md': {'content': "---\nauthor: null\ncreated: 2013-09-23 09:20:50-07:00\nid: '20130923092050'\ntitle: At in tellus lectus arcu bibendum at varius\n---\n# At in tellus lectus arcu bibendum at varius\n\nMassa nullam ac tortor vitae purus faucibus quis hendrerit dolor magna eget.  Felis bibendum ut tristique libero enim sed faucibus turpis in eu mi.  Cursus mattis molestie tincidunt vitae semper quis lectus nulla at volutpat pellentesque nec nam aliquam sem et tortor amet nisl purus in mollis ullamcorper malesuada proin libero nunc.  Hendrerit dolor magna eget est lorem ipsum cursus mattis molestie a iaculis at erat pellentesque pellentesque elit eget gravida cum vel orci.  Suspendisse faucibus interdum posuere lorem placerat.\n\n", 'modified': 1379953250},
   '/alpha/missing-created.md': {'content': '---\nauthor: Dave Davidson\ncreated: null\nid: null\ntitle: Feugiat in ante enim neque volutpat ac\n---\n# Feugiat in ante enim neque volutpat ac\n\nConsequat semper viverra nam libero justo laoreet nunc vel risus commodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque id ornare arcu dui vivamus arcu.  Donec enim in nibh mauris.\n\n', 'modified': 685551690},
   '/alpha/missing-id.md': {'content': '---\nauthor: Fiona Fiorella\ncreated: 2004-09-17 03:22:20+03:00\nid: null\ntitle: A iaculis at erat\n---\n# A iaculis at erat\n\nAliquet risus libero id faucibus nisl tincidunt eget nullam et ligula ullamcorper malesuada proin in.  Vestibulum ac auctor augue mauris augue neque gravida in magna etiam tempor orci eu lobortis elementum nibh tellus molestie massa sapien.\n\n', 'modified': 1095380540},
   '/alpha/missing-title.md': {'content': "---\nauthor: Eva Evanston\ncreated: 2008-10-14 00:51:49+02:00\nid: '20081014005149'\ntitle: null\n---\n# Euismod in est ante in\n\nRisus sed vulputate odio at risus viverra adipiscing at in tellus lectus arcu bibendum at varius vel pharetra vel amet.  Dui lacus sed turpis tincidunt.  Mauris cursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat vestibulum lectus mauris.  Phasellus vestibulum lorem sed risus sed cras ornare arcu dui vivamus arcu lectus.  Tincidunt id aliquet risus feugiat.\n\nLigula ullamcorper malesuada proin in nibh mauris cursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat vestibulum.\n\nOdio tempus egestas sed sed risus vivamus.  Proin libero nunc consequat interdum varius tincidunt id aliquet risus feugiat in ante enim neque.  Diam phasellus vestibulum lorem sed risus ultricies tristique nulla odio aenean sed adipiscing diam in est ante in nibh quisque non tellus orci ac.\n\n", 'modified': 1223938309},
}

# This mock filesystem contains three folders and a total of four notes that all have the same ID. Two of the conflicts
# are in the "bravo" folder, and one is in each of the "charlie" and "delta" folders. The echo folder has three notes
# with no ID and should be used to test if null IDs are detected as conflicts
INDEX_WITH_CONFLICTS = {
   '/bravo/note-00.md': {'content': "---\nauthor: Charles Charleston\ncreated: 2009-09-04 12:59:15+06:00\nid: '20090904125915'\ntitle: Nulla at volutpat pellentesque nec\n---\n# Nulla at volutpat pellentesque nec\n\nGravida in magna etiam tempor orci eu lobortis elementum nibh.  Dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ullamcorper dignissim cras tincidunt lobortis sit amet volutpat consequat mauris auctor neque vitae.  Nisl tincidunt eget nullam non nisi est non quam lacus suspendisse faucibus interdum posuere lorem placerat vestibulum lectus mauris ultrices eros.  Nisl tincidunt eget nullam et ligula ullamcorper malesuada proin in nibh mauris cursus mattis molestie a iaculis ultrices eros in cursus turpis.\n\nNam aliquam sem et tortor amet nisl purus in mollis ullamcorper malesuada proin libero nunc consequat interdum varius tincidunt id aliquet risus feugiat in ante.  Cursus mattis molestie a iaculis at erat pellentesque pellentesque elit eget gravida cum vel orci.  Lacus viverra vitae congue cras adipiscing enim eu turpis egestas pretium euismod lacinia at quis risus sed vulputate odio at risus viverra adipiscing at in.  Cum vel orci porta non.  Lectus vestibulum ac auctor augue mauris augue neque gravida in magna etiam tempor orci eu lobortis elementum nibh tellus molestie massa sapien faucibus.\n\nCursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat vestibulum lectus mauris auctor.\n\n", 'modified': 1252047555},
   '/bravo/note-01.md': {'content': "---\nauthor: Charles Charleston\ncreated: 1991-11-06 22:03:10+02:00\nid: '19911106220310'\ntitle: Viverra adipiscing at in tellus lectus\n---\n# Viverra adipiscing at in tellus lectus\n\nNulla at volutpat pellentesque nec nam aliquam sem et.  Morbi tincidunt augue interdum velit euismod in est ante in nibh mauris cursus mattis.  Varius quam quisque id ornare arcu dui vivamus arcu felis bibendum faucibus a pellentesque sit amet.  Lacinia at quis risus sed vulputate odio at risus viverra adipiscing at in tellus lectus arcu.\n\n", 'modified': 689457790},
   '/bravo/note-02.md': {'content': "---\nauthor: Alice Allison\ncreated: 1996-12-12 09:33:32+08:00\nid: '19961212093332'\ntitle: In cursus turpis massa tincidunt id\n---\n# In cursus turpis massa tincidunt id\n\nAc feugiat sed lectus vestibulum ac auctor augue mauris augue neque gravida in magna.  Felis bibendum ut tristique libero enim sed faucibus turpis in eu mi bibendum neque morbi tincidunt augue.  Imperdiet dui lacus sed turpis tincidunt id aliquet risus libero id faucibus.  Vulputate mi morbi blandit cursus risus at ultrices mi tempus imperdiet nulla a cras semper auctor neque vitae tempus quam ut consequat semper viverra nam.  Lectus vestibulum ac auctor augue mauris augue neque gravida in magna etiam tempor orci eu lobortis elementum nibh tellus molestie massa sapien faucibus et.\n\nVel risus commodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque id ornare arcu dui.  Molestie tincidunt vitae semper quis lectus nulla at volutpat pellentesque nec nam aliquam sem et tortor amet nisl.  Lacus viverra vitae congue cras adipiscing enim eu turpis egestas pretium euismod lacinia at quis risus sed vulputate odio at risus viverra adipiscing at in tellus.  Tempor incididunt ut labore et dolore magna.\n\nUt tristique libero enim sed faucibus turpis in eu mi bibendum neque morbi tincidunt augue interdum velit euismod in est ante in nibh mauris.  Massa tincidunt id faucibus nisl tincidunt eget nullam non nisi est non quam lacus suspendisse faucibus interdum posuere lorem placerat vestibulum lectus mauris ultrices.  At quis risus sed vulputate odio at risus viverra adipiscing at in tellus lectus arcu bibendum at varius.  At quis risus sed vulputate odio tempus egestas sed sed risus vivamus arcu.  Lorem placerat vestibulum lectus mauris ultrices eros in cursus turpis massa nullam ac tortor vitae purus faucibus quis hendrerit dolor.\n\n", 'modified': 850354412},
   '/charlie/note-00.md': {'content': "---\nauthor: Fiona Fiorella\ncreated: 1990-12-28 20:59:35+06:00\nid: '19901228205935'\ntitle: Nam libero justo laoreet nunc\n---\n# Nam libero justo laoreet nunc\n\nDolore magna aliqua ullamcorper dignissim cras tincidunt lobortis sit.  Elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ullamcorper dignissim cras.  Odio at risus viverra adipiscing at in tellus lectus arcu bibendum at varius vel pharetra.  Viverra adipiscing at in tellus lectus arcu bibendum at varius vel pharetra vel amet dictum sit amet justo donec.\n\nHendrerit dolor magna eget est lorem ipsum faucibus et molestie ac feugiat sed lectus vestibulum ac auctor augue mauris augue neque gravida in magna etiam tempor orci eu.  Mauris auctor neque vitae tempus quam phasellus vestibulum lorem sed risus sed cras ornare arcu dui vivamus arcu lectus mauris ultrices eros in cursus turpis massa.  Eiusmod tempor incididunt ut labore et dolore magna aliqua ullamcorper dignissim cras tincidunt lobortis sit amet volutpat consequat mauris auctor neque vitae.  Elit at imperdiet dui lacus sed turpis tincidunt id aliquet risus.\n\n", 'modified': 662396375},
   '/charlie/note-01.md': {'content': "---\nauthor: Eva Evanston\ncreated: 1994-02-22 13:51:18-03:00\nid: '19940222135118'\ntitle: Aliquet risus libero id faucibus nisl tincidunt eget\n---\n# Aliquet risus libero id faucibus nisl tincidunt eget\n\nOrci eu lobortis elementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc.\n\n", 'modified': 761935878},
   '/charlie/note-02.md': {'content': "---\nauthor: Fiona Fiorella\ncreated: 1995-04-20 07:20:11+02:00\nid: '19950420072011'\ntitle: In cursus turpis\n---\n# In cursus turpis\n\nArcu bibendum at varius vel pharetra vel amet dictum sit amet justo donec enim in nibh mauris.  Faucibus turpis in eu mi bibendum neque morbi tincidunt augue.  Dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt.  Sed vulputate odio tempus egestas sed.\n\n", 'modified': 798355211},
   '/delta/note-00.md': {'content': "---\nauthor: Alice Allison\ncreated: 1996-07-29 20:12:32+10:00\nid: '19960729201232'\ntitle: Ante enim neque volutpat ac tincidunt\n---\n# Ante enim neque volutpat ac tincidunt\n\nNibh mauris cursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean.  Ultrices eros in cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat vestibulum lectus mauris auctor elit sed.  Do eiusmod tempor incididunt ut labore et dolore magna aliqua ullamcorper dignissim cras tincidunt lobortis sit amet.\n\n", 'modified': 838635152},
   '/delta/note-01.md': {'content': "---\nauthor: Charles Charleston\ncreated: 2000-10-09 03:52:58-04:00\nid: '20001009035258'\ntitle: Mi morbi blandit\n---\n# Mi morbi blandit\n\nMi quis hendrerit dolor magna eget est lorem ipsum faucibus et molestie ac feugiat sed lectus vestibulum ac auctor augue mauris augue neque gravida in magna etiam.\n\nSed vulputate odio tempus egestas sed sed.\n\n", 'modified': 971077978},
   '/delta/note-02.md': {'content': "---\nauthor: Charles Charleston\ncreated: 2005-09-09 08:08:00+03:00\nid: '20050909080800'\ntitle: Felis bibendum ut tristique libero enim\n---\n# Felis bibendum ut tristique libero enim\n\nAenean sed adipiscing diam in est ante in nibh.\n\nVarius vel pharetra vel amet dictum sit amet justo donec enim in nibh mauris cursus mattis molestie a iaculis at erat neque gravida in fermentum et.  Sed risus ultricies tristique nulla odio aenean sed adipiscing diam in est ante.  Faucibus nisl tincidunt eget nullam non nisi est non quam lacus suspendisse faucibus.  Iaculis at erat pellentesque adipiscing commodo elit at imperdiet dui lacus sed turpis tincidunt id.  Et at quis risus sed vulputate odio tempus egestas sed sed risus vivamus arcu felis bibendum.\n\nTempus quam ut consequat semper viverra nam libero justo laoreet nunc vel risus.  Consequat semper viverra nam libero justo laoreet nunc vel risus commodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque id ornare arcu dui vivamus arcu felis bibendum faucibus.\n\n", 'modified': 1126242480},
   '/bravo/conflict-00.md': {'content': "---\nauthor: Dave Davidson\ncreated: 2007-11-16 15:16:27+08:00\nid: '20071116151627'\ntitle: Ornare arcu dui vivamus\n---\n# Ornare arcu dui vivamus\n\nElit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ullamcorper dignissim cras tincidunt lobortis sit amet volutpat consequat mauris auctor neque.  Augue interdum velit euismod in est ante in nibh mauris cursus mattis molestie tincidunt vitae semper quis lectus nulla at volutpat pellentesque nec nam aliquam sem et tortor.  Nulla odio aenean sed adipiscing diam in est ante in nibh quisque non.\n\nAt quis risus sed vulputate odio tempus egestas sed sed risus vivamus arcu felis bibendum ut tristique libero enim sed.\n\n", 'modified': 1195197387},
   '/bravo/conflict-01.md': {'content': "---\nauthor: Alice Allison\ncreated: 2007-11-16 15:16:27+08:00\nid: '20071116151627'\ntitle: Nullam non nisi est non quam lacus\n---\n# Nullam non nisi est non quam lacus\n\nIn est ante in nibh quisque non.  Elit at imperdiet dui lacus sed turpis tincidunt id aliquet risus libero id faucibus nisl tincidunt eget nullam et ligula ullamcorper malesuada.  Ac placerat vestibulum lectus mauris auctor elit sed vulputate mi morbi blandit cursus risus at ultrices mi tempus imperdiet nulla a cras.  Diam phasellus vestibulum lorem sed risus ultricies tristique nulla odio aenean sed adipiscing diam in est ante in nibh.  Cursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat vestibulum lectus mauris auctor elit sed vulputate mi morbi blandit cursus.\n\n", 'modified': 1195197387},
   '/charlie/conflict.md': {'content': "---\nauthor: Fiona Fiorella\ncreated: 2007-11-16 15:16:27+08:00\nid: '20071116151627'\ntitle: Risus ultricies tristique nulla odio aenean sed adipiscing\n---\n# Risus ultricies tristique nulla odio aenean sed adipiscing\n\nRisus vivamus arcu felis bibendum ut tristique libero enim sed faucibus turpis in eu mi bibendum neque morbi tincidunt augue interdum velit euismod in est ante in nibh mauris.  Pellentesque sit amet porttitor diam phasellus vestibulum lorem sed risus ultricies tristique nulla odio aenean sed.  Enim in nibh mauris cursus mattis molestie a iaculis.\n\nIaculis at erat pellentesque adipiscing commodo elit.  A iaculis at erat neque gravida in fermentum et at quis risus sed vulputate odio tempus.  Nam aliquam sem et tortor amet nisl purus in mollis ullamcorper malesuada proin libero nunc consequat interdum varius tincidunt.\n\n", 'modified': 1195197387},
   '/delta/conflict.md': {'content': "---\nauthor: Eva Evanston\ncreated: 2007-11-16 15:16:27+08:00\nid: '20071116151627'\ntitle: Enim neque volutpat ac tincidunt vitae semper\n---\n# Enim neque volutpat ac tincidunt vitae semper\n\nEst ante in nibh mauris cursus mattis molestie tincidunt.\n\nOrnare arcu dui vivamus arcu felis bibendum faucibus a pellentesque sit amet porttitor diam phasellus vestibulum lorem sed risus ultricies tristique nulla odio aenean.  Lectus nulla at volutpat pellentesque nec nam aliquam sem et tortor.  Faucibus interdum posuere lorem placerat vestibulum lectus mauris ultrices eros in cursus turpis massa nullam ac tortor vitae purus faucibus quis hendrerit dolor magna eget est.  Amet justo donec enim in nibh mauris cursus mattis molestie.\n\n", 'modified': 1195197387},
   '/echo/note-00.md': {'content': "---\nauthor: Charles Charleston\ncreated: 2016-09-26 02:29:08+06:30\nid: '20160926022908'\ntitle: Gravida in fermentum et at quis\n---\n# Gravida in fermentum et at quis\n\nBibendum faucibus a pellentesque sit amet porttitor diam phasellus vestibulum lorem sed risus.  Dignissim cras tincidunt lobortis sit amet volutpat consequat mauris auctor neque vitae.  Mattis molestie tincidunt vitae semper quis lectus nulla at volutpat pellentesque nec nam aliquam sem et tortor amet nisl purus in mollis ullamcorper malesuada proin libero.  Semper auctor neque vitae tempus quam ut consequat semper viverra nam libero justo laoreet nunc vel risus commodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque.  At volutpat pellentesque nec nam aliquam sem et tortor amet nisl purus in mollis ullamcorper malesuada proin libero nunc consequat interdum varius tincidunt id aliquet risus feugiat in ante.\n\nNulla a cras semper auctor neque vitae tempus quam ut consequat semper viverra nam libero justo.  A iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean.  Risus sed vulputate odio tempus egestas sed sed risus vivamus arcu felis bibendum ut tristique libero enim sed faucibus turpis in eu mi bibendum neque morbi tincidunt augue.  Ac feugiat sed lectus vestibulum ac auctor augue mauris augue neque gravida in magna etiam tempor orci eu lobortis.\n\nEget nullam non nisi est non quam lacus suspendisse faucibus interdum posuere lorem placerat vestibulum lectus mauris ultrices eros in cursus turpis massa nullam ac tortor vitae.  Magna etiam tempor orci eu lobortis elementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper.  Turpis in eu mi bibendum neque morbi tincidunt augue interdum velit euismod in est ante in nibh mauris cursus mattis molestie tincidunt vitae semper quis lectus nulla at volutpat.\n\n", 'modified': 1474833548},
   '/echo/note-01.md': {'content': "---\nauthor: Fiona Fiorella\ncreated: 2009-03-18 16:57:37+11:00\nid: '20090318165737'\ntitle: Ullamcorper dignissim cras tincidunt lobortis\n---\n# Ullamcorper dignissim cras tincidunt lobortis\n\nTempor orci eu lobortis elementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue.  Id faucibus nisl tincidunt eget.  Augue neque gravida in magna etiam tempor.  Quisque id ornare arcu dui vivamus arcu felis bibendum faucibus a pellentesque sit.\n\nMassa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue lacus viverra vitae congue cras adipiscing enim eu.  Imperdiet dui lacus sed turpis tincidunt id aliquet risus libero id faucibus nisl tincidunt eget.\n\nMagna etiam tempor orci eu lobortis elementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat ligula.\n\n", 'modified': 1237355857},
   '/echo/note-02.md': {'content': "---\nauthor: Fiona Fiorella\ncreated: 2000-07-08 00:35:49-04:00\nid: '20000708003549'\ntitle: In eu mi bibendum neque morbi tincidunt\n---\n# In eu mi bibendum neque morbi tincidunt\n\nLorem placerat vestibulum lectus mauris ultrices eros in cursus turpis massa nullam ac tortor vitae purus faucibus quis hendrerit dolor magna eget est lorem ipsum.\n\nNon quam lacus suspendisse faucibus interdum posuere lorem placerat vestibulum lectus mauris ultrices eros in cursus turpis massa nullam ac tortor vitae purus faucibus quis hendrerit dolor magna eget est.\n\nMassa nullam ac tortor vitae purus faucibus quis hendrerit dolor magna eget est.  Proin in nibh mauris cursus mattis molestie a iaculis ultrices eros in cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat.  In cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat vestibulum lectus.  Id aliquet risus libero id faucibus nisl tincidunt eget nullam et ligula ullamcorper malesuada proin in nibh mauris cursus.\n\n", 'modified': 963030949},
   '/echo/note-03.md': {'content': '---\nauthor: Eva Evanston\ncreated: 2003-05-04 00:16:31+03:00\nid: null\ntitle: Mattis molestie tincidunt vitae semper quis lectus nulla\n---\n# Mattis molestie tincidunt vitae semper quis lectus nulla\n\nElementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat.  Id aliquet risus feugiat in.\n\nLobortis elementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada.  Vitae purus faucibus quis hendrerit dolor magna eget est lorem ipsum cursus mattis molestie a iaculis at erat pellentesque pellentesque elit eget gravida cum vel orci porta non pulvinar.  At erat pellentesque adipiscing commodo elit at imperdiet dui lacus sed turpis tincidunt id aliquet risus libero id faucibus nisl.  Tortor amet nisl purus in mollis ullamcorper malesuada.\n\nVel risus commodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque id ornare arcu dui vivamus arcu felis bibendum faucibus a.  Turpis tincidunt id aliquet risus libero id faucibus nisl tincidunt eget nullam et ligula ullamcorper malesuada proin in nibh mauris cursus mattis molestie.  Magna eget est lorem ipsum cursus mattis molestie a iaculis at erat pellentesque pellentesque elit eget gravida.\n\n', 'modified': 1051996591},
   '/echo/note-04.md': {'content': '---\nauthor: Fiona Fiorella\ncreated: 2021-01-24 05:28:08-05:00\nid: null\ntitle: Nibh tellus molestie massa sapien\n---\n# Nibh tellus molestie massa sapien\n\nOrnare arcu dui vivamus arcu lectus mauris ultrices eros in cursus turpis massa tincidunt id faucibus nisl tincidunt eget nullam non nisi est non quam lacus suspendisse faucibus interdum.  Ac tincidunt vitae semper quis lectus at consectetur lorem donec massa sapien faucibus et.  Ultricies tristique nulla odio aenean sed adipiscing diam in est.\n\nPosuere lorem placerat vestibulum lectus mauris ultrices eros in cursus turpis massa nullam ac tortor.  Molestie a iaculis at erat pellentesque pellentesque elit eget gravida cum vel orci porta non pulvinar neque laoreet suspendisse iaculis at erat pellentesque adipiscing commodo elit at imperdiet dui lacus.  Vitae tempus quam phasellus vestibulum lorem.  Augue neque gravida in magna etiam.  Cursus turpis massa tincidunt dui ut aenean pharetra magna ac placerat.\n\n', 'modified': 1611484088},
   '/echo/note-05.md': {'content': '---\nauthor: Alice Allison\ncreated: 1993-03-20 01:11:14-10:00\nid: null\ntitle: Phasellus vestibulum lorem\n---\n# Phasellus vestibulum lorem\n\nNon quam lacus suspendisse faucibus interdum posuere lorem placerat vestibulum lectus mauris ultrices eros in cursus turpis massa nullam ac tortor vitae purus faucibus quis hendrerit dolor magna eget.  Tincidunt vitae semper quis lectus nulla at volutpat pellentesque nec nam aliquam.  Magna ac placerat vestibulum lectus mauris auctor elit sed vulputate mi morbi blandit cursus risus at ultrices mi tempus imperdiet nulla a cras semper auctor.  Elementum nibh tellus molestie massa sapien faucibus et molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue lacus.  Bibendum ut tristique libero enim sed faucibus turpis in.\n\n', 'modified': 732625874},
}

# This index contains notes with links between them, and the links are included in the link dictionary below
INDEX_WITH_LINKS = {
   '/links/note-00.md': {'content': "---\nauthor: Bob Bobertsmith\ncreated: 2017-06-09 08:38:41+00:00\nid: '20170609083841'\ntitle: Consequat mauris auctor neque vitae tempus\n---\n# Consequat mauris auctor neque vitae tempus\n\nVulputate odio tempus egestas sed sed risus vivamus arcu felis bibendum ut tristique libero enim sed faucibus turpis in.\n\nUllamcorper malesuada proin libero iaculis nunc sed augue lacus viverra [[19910802211642]] vitae congue cras adipiscing enim eu turpis egestas pretium euismod.  Ullamcorper dignissim cras tincidunt lobortis sit amet volutpat consequat mauris auctor neque vitae tempus.  Bibendum neque morbi tincidunt augue.  Lorem sed risus sed cras ornare arcu dui vivamus arcu lectus mauris ultrices eros in cursus turpis massa tincidunt id faucibus nisl tincidunt eget nullam non nisi est non quam.\n\n", 'modified': 1496997521},
   '/links/note-01.md': {'content': "---\nauthor: Eva Evanston\ncreated: 2003-11-27 10:37:17+02:00\nid: '20031127103717'\ntitle: Et dolore magna aliqua ullamcorper\n---\n# Et dolore magna aliqua ullamcorper\n\nTincidunt lobortis sit amet volutpat consequat mauris auctor neque vitae tempus quam phasellus vestibulum [[20201204110546]] lorem sed risus sed [[20160227182247]] cras ornare arcu dui vivamus arcu lectus mauris ultrices eros in.\n\nMauris cursus mattis molestie a iaculis at erat neque.  Molestie ac feugiat ligula ullamcorper malesuada proin libero iaculis nunc sed augue lacus viverra vitae congue cras.\n\n", 'modified': 1069922237},
   '/links/note-02.md': {'content': "---\nauthor: Fiona Fiorella\ncreated: 2020-12-04 11:05:46+01:00\nid: '20201204110546'\ntitle: Diam phasellus vestibulum lorem sed risus\n---\n# Diam phasellus vestibulum lorem sed risus\n\nRisus commodo viverra maecenas accumsan lacus vel facilisis quis varius quam quisque id ornare arcu dui vivamus arcu felis bibendum [[19910802211642]] faucibus a pellentesque sit.  Sit amet justo donec enim in nibh mauris.\n\n", 'modified': 1607076346},
   '/links/note-03.md': {'content': "---\nauthor: Dave Davidson\ncreated: 2016-02-27 18:22:47+07:00\nid: '20160227182247'\ntitle: Non quam lacus suspendisse\n---\n# Non quam lacus suspendisse\n\nRisus sed vulputate odio tempus egestas sed sed [[20201204110546]] risus vivamus arcu felis bibendum ut tristique libero.  Sed cras ornare arcu dui vivamus arcu lectus mauris ultrices eros in cursus turpis massa tincidunt id.  Ipsum faucibus et molestie ac feugiat sed lectus vestibulum ac auctor augue mauris augue neque.  Nulla a cras semper auctor neque vitae tempus quam ut consequat semper viverra nam.  Ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt.\n\n", 'modified': 1456572167},
   '/links/note-04.md': {'content': "---\nauthor: Charles Charleston\ncreated: 1991-08-02 21:16:42-03:00\nid: '19910802211642'\ntitle: Lorem placerat vestibulum lectus mauris ultrices eros\n---\n# Lorem placerat vestibulum lectus mauris ultrices eros\n\nSed vulputate odio at risus viverra adipiscing at in tellus lectus arcu bibendum at varius vel pharetra vel amet dictum sit.  Erat pellentesque pellentesque [[20160227182247]] elit eget.  Eget est lorem ipsum cursus mattis molestie a iaculis at erat pellentesque pellentesque elit eget gravida cum vel orci.\n\n", 'modified': 681178602},
}

INDEX_WITH_LINKS_LINKS = {'20170609083841': ['19910802211642'], '20031127103717': ['20201204110546', '20160227182247'], '20201204110546': ['19910802211642'], '20160227182247': ['20201204110546'], '19910802211642': ['20160227182247']}