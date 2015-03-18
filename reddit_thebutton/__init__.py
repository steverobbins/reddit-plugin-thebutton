from r2.lib.configparse import ConfigValue
from r2.lib.js import Module
from r2.lib.plugin import Plugin


class TheButton(Plugin):
    needs_static_build = True

    config = {
        ConfigValue.tuple: [
            "thebutton_caches",
        ],
        ConfigValue.int: [
            "thebutton_srid",
        ],
    }

    live_config = {
        ConfigValue.str: [
            "thebutton_id",
        ],
    }

    js = {
        "thebutton": Module("thebutton.js",
            "websocket.js",
            "thebutton.js",
        )
    }

    def on_load(self, g):
        from r2.lib.cache import CMemcache, MemcacheChain, LocalCache, SelfEmptyingCache

        thebutton_memcaches = CMemcache(
            'thebutton',
            g.thebutton_caches,
            num_clients=g.num_mc_clients,
        )
        localcache_cls = (SelfEmptyingCache if g.running_as_script else LocalCache)
        g.thebuttoncache = MemcacheChain((
            localcache_cls(),
            thebutton_memcaches,
        ))
        g.cache_chains.update(thebutton=g.thebuttoncache)

    def add_routes(self, mc):
        mc(
            "/api/press_button",
            controller="buttonapi",
            action="press_button",
        )

        mc(
            "/thebutton",
            controller="button",
            action="button",
        )

    def load_controllers(self):
        from reddit_thebutton.controllers import (
            ButtonApiController,
            ButtonController,
        )

        from reddit_thebutton.hooks import hooks
        hooks.register_all()