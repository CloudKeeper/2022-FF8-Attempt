"""
Batchcode for testing purposes.

"""

from evennia.utils import create, search

# obj = create.create_object(key="test", location=caller.location)
# obj.locks.add("search:false()")
# obj.locks.add("view:false()")

# if obj.access(obj, 'search'):
#     caller.msg("search allowed")
# if not obj.access(obj, 'search'):
#     caller.msg("search not allowed")

# results = caller.location.contents
# if search.objects("Ben") :
#     caller.msg("Found Ben")
# for obj in [x for x in results if x.access(search.objects("Ben"), "search")]:
#     caller.msg(obj.key + " passed")