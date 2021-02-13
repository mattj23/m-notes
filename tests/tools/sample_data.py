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
author: Alice Alisson
created: '2021-02-13T16:06:41.927650-05:00'
id: 20210213160641
...
# Sample Note 1

This is some text in the sample note 1
"""

