odoo.define('website_dashboard_tile.tile', function (require) {
    "use strict";

    var ActionManager = require('web.ActionManager');
    var Context = require('web.Context');
    var core = require('web.core');
    var Domain = require('web.Domain');
    var FavoriteMenu = require('web.FavoriteMenu');
    var pyeval = require('web.pyeval');
    var ViewManager = require('web.ViewManager');
    var session = require('web.session');

    var _t = core._t;
    var QWeb = core.qweb;

    FavoriteMenu.include({
        /**
         * We manually add the 'add to dashboard tile' feature in the searchview.
         *
         * @override
         */
        start: function () {
            this._super();
            var self = this;
            // if(this.action_id === undefined) {
            //     return this._super();
            // }
            var am = this.findAncestor(function (a) {
                return a instanceof ActionManager;
            });
            if (am && am.get_inner_widget() instanceof ViewManager) {
                this.view_manager = am.get_inner_widget();
                this.add_to_dashboard_tile_available = true;
                this.$('.o_favorites_menu').append(QWeb.render('SearchView.addtodashboardtile'));
                this.$add_to_dashboard_tile = this.$('.o_add_to_dashboard_tile');
                this.$add_dashboard_tile_btn = this.$add_to_dashboard_tile.eq(1).find('button');
                this.$add_dashboard_tile_input = this.$add_to_dashboard_tile.eq(0).find('input');
                this.$add_dashboard_tile_link = this.$('.o_add_to_dashboard_tile_link');
                var title = this.searchview.get_title();
                this.$add_dashboard_tile_input.val(title);
                this.$add_dashboard_tile_link.click(function (e) {
                    e.preventDefault();
                    self._toggleDashboardTileMenu();
                });
                this.$add_dashboard_tile_btn.click(this.proxy('_addDashboardTile'));
            }
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * This is the main function for actually saving the dashboard. This method
         * is supposed to call the route /board/add_to_dashboard with proper
         * information.
         *
         * @private
         * @returns {Deferred}
         */
        _addDashboardTile: function () {
            console.log("_addDashboardTile");
            var self = this;
            var search_data = this.searchview.build_search_data();
            var context = new Context(this.searchview.dataset.get_context() || []);
            var domain = this.searchview.dataset.get_domain() || [];

            _.each(search_data.contexts, context.add, context);
            _.each(search_data.domains, function (d) {
                domain.push.apply(domain, Domain.prototype.stringToArray(d));
            });

            context.add({
                group_by: pyeval.eval('groupbys', search_data.groupbys || [])
            });
            context.add(this.view_manager.active_view.controller.getContext());
            var c = pyeval.eval('context', context);
            for (var k in c) {
                if (c.hasOwnProperty(k) && /^search_default_/.test(k)) {
                    delete c[k];
                }
            }
            this._toggleDashboardTileMenu(false);
            c.dashboard_merge_domains_contexts = false;

            var name = self.$add_dashboard_tile_input.val();

            var private_filter = !this.$('#oe_searchview_custom_public').prop('checked');
            if (_.isEmpty(name)){
                this.do_warn(_t("Error"), _t("Filter name is required."));
                return false;
            }

            // Don't save user_context keys in the custom filter, otherwise end
            // up with e.g. wrong uid or lang stored *and used in subsequent
            // reqs*
            var ctx = context;
            _(_.keys(session.user_context)).each(function (key) {
                delete ctx[key];
            });

            return self._rpc({
                    route: '/board/add_to_dashboard_tile',
                    params: {
                        action_id: self.action_id || false,
                        domain: domain,
                        view_mode: self.view_manager.active_view.type,
                        name: name,
                        user_id: private_filter ? session.uid : false,
                        model_name: self.view_manager.active_view.controller.modelName,
                    },
                })
                .then(function (r) {
                    if (r) {
                        self.do_notify(
                            _.str.sprintf(_t("'%s' added to dashboard tile"), name)
                        );
                    } else {
                        self.do_warn(_t("Could not add filter to dashboard tile"));
                    }
                });
        },
        /**
         * @override
         * @private
         */
        _closeMenus: function () {
            if (this.add_to_dashboard_tile_available) {
                this._toggleDashboardTileMenu(false);
            }
            this._super();
        },
        /**
         * @private
         * @param {undefined|false} isOpen
         */
        _toggleDashboardTileMenu: function (isOpen) {
            this.$add_dashboard_tile_link
                .toggleClass('o_closed_menu', !(_.isUndefined(isOpen)) ? !isOpen : undefined)
                .toggleClass('o_open_menu', isOpen);
            this.$add_to_dashboard_tile.toggle(isOpen);
            if (this.$add_dashboard_tile_link.hasClass('o_open_menu')) {
                this.$add_dashboard_tile_input.focus();
            }
        },
    });
});
