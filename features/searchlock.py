"""
This is a Character typeclass 
"""

from django.conf import settings
from evennia import DefaultCharacter
from evennia.objects.models import ObjectDB
from evennia.utils.utils import make_iter, variable_from_module

_AT_SEARCH_RESULT = variable_from_module(*settings.SEARCH_AT_RESULT.rsplit(".", 1))

class SearchLockCharacter(DefaultCharacter):
    def search(
        self,
        searchdata,
        global_search=False,
        use_nicks=True,
        typeclass=None,
        location=None,
        attribute_name=None,
        quiet=False,
        exact=False,
        candidates=None,
        use_locks=True,
        nofound_string=None,
        multimatch_string=None,
        use_dbref=None,
    ):
        """
        Returns an Object matching a search string/condition

        Perform a standard object search in the database, handling
        multiple results and lack thereof gracefully. By default, only
        objects in the current `location` of `self` or its inventory are searched for.

        Args:
            searchdata (str or obj): Primary search criterion. Will be matched
                against `object.key` (with `object.aliases` second) unless
                the keyword attribute_name specifies otherwise.

                Special strings:

                - `#<num>`: search by unique dbref. This is always
                   a global search.
                - `me,self`: self-reference to this object
                - `<num>-<string>` - can be used to differentiate
                   between multiple same-named matches. The exact form of this input
                   is given by `settings.SEARCH_MULTIMATCH_REGEX`.

            global_search (bool): Search all objects globally. This overrules 'location' data.
            use_nicks (bool): Use nickname-replace (nicktype "object") on `searchdata`.
            typeclass (str or Typeclass, or list of either): Limit search only
                to `Objects` with this typeclass. May be a list of typeclasses
                for a broader search.
            location (Object or list): Specify a location or multiple locations
                to search. Note that this is used to query the *contents* of a
                location and will not match for the location itself -
                if you want that, don't set this or use `candidates` to specify
                exactly which objects should be searched.
            attribute_name (str): Define which property to search. If set, no
                key+alias search will be performed. This can be used
                to search database fields (db_ will be automatically
                prepended), and if that fails, it will try to return
                objects having Attributes with this name and value
                equal to searchdata. A special use is to search for
                "key" here if you want to do a key-search without
                including aliases.
            quiet (bool): don't display default error messages - this tells the
                search method that the user wants to handle all errors
                themselves. It also changes the return value type, see
                below.
            exact (bool): if unset (default) - prefers to match to beginning of
                string rather than not matching at all. If set, requires
                exact matching of entire string.
            candidates (list of objects): this is an optional custom list of objects
                to search (filter) between. It is ignored if `global_search`
                is given. If not set, this list will automatically be defined
                to include the location, the contents of location and the
                caller's contents (inventory).
            use_locks (bool): If True (default) - removes search results which
                fail the "search" lock.
            nofound_string (str):  optional custom string for not-found error message.
            multimatch_string (str): optional custom string for multimatch error header.
            use_dbref (bool or None, optional): If `True`, allow to enter e.g. a query "#123"
                to find an object (globally) by its database-id 123. If `False`, the string "#123"
                will be treated like a normal string. If `None` (default), the ability to query by
                #dbref is turned on if `self` has the permission 'Builder' and is turned off
                otherwise.

        Returns:
            Object, None or list: Will return an `Object` or `None` if `quiet=False`. Will return a
            list with 0, 1 or more matches if `quiet=True`. If `stacked` is a positive integer, this
            list may contain all stacked identical matches.

        Notes:
            To find Accounts, use eg. `evennia.account_search`. If
            `quiet=False`, error messages will be handled by
            `settings.SEARCH_AT_RESULT` and echoed automatically (on
            error, return will be `None`). If `quiet=True`, the error
            messaging is assumed to be handled by the caller.

        """
        is_string = isinstance(searchdata, str)

        if is_string:
            # searchdata is a string; wrap some common self-references
            if searchdata.lower() in ("here",):
                return [self.location] if quiet else self.location
            if searchdata.lower() in ("me", "self"):
                return [self] if quiet else self

        if use_dbref is None:
            use_dbref = self.locks.check_lockstring(self, "_dummy:perm(Builder)")

        if use_nicks:
            # do nick-replacement on search
            searchdata = self.nicks.nickreplace(
                searchdata, categories=("object", "account"), include_account=True
            )

        if global_search or (
            is_string
            and searchdata.startswith("#")
            and len(searchdata) > 1
            and searchdata[1:].isdigit()
        ):
            # only allow exact matching if searching the entire database
            # or unique #dbrefs
            exact = True
            candidates = None

        elif candidates is None:
            # no custom candidates given - get them automatically
            if location:
                # location(s) were given
                candidates = []
                for obj in make_iter(location):
                    candidates.extend(obj.contents)
            else:
                # local search. Candidates are taken from
                # self.contents, self.location and
                # self.location.contents
                location = self.location
                candidates = self.contents
                if location:
                    candidates = candidates + [location] + location.contents
                else:
                    # normally we don't need this since we are
                    # included in location.contents
                    candidates.append(self)

        results = ObjectDB.objects.object_search(
            searchdata,
            attribute_name=attribute_name,
            typeclass=typeclass,
            candidates=candidates,
            exact=exact,
            use_dbref=use_dbref,
        )
        
        results = list(results)
        
        # Added to remove objects that do not have the search permission
        if use_locks:
            results = [x for x in results if x.access(self, "search")]
        
        if quiet:
            return results
            
        return _AT_SEARCH_RESULT(
            results,
            self,
            query=searchdata,
            nofound_string=nofound_string,
            multimatch_string=multimatch_string,
        )