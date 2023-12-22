class DBRouter:
    route_model_names = ("Subscription", "Account", "IntermediateSubscription")

    def db_for_read(self, model, **hints):
        if model._meta.object_name in self.route_model_names:
            return "splay"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.object_name in self.route_model_names:
            return "splay"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True if obj1._meta.object_name in self.route_model_names or obj2._meta.object_name in self.route_model_names else None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "splay":
            if model_name in self.route_model_names:
                return True
            return False
        else:
            if model_name in self.route_model_names:
                return False
            return True
