class ShopRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'shop':
            return 'shop'
        return None


    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'shop':
            return 'shop'
        return None


    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'shop' or obj2._meta.app_label == 'shop':
            return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'shop':
            return db == 'shop'
        return None


class UserRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'user':
            return 'user'
        return None


    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'user':
            return 'user'
        return None


    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'user' or obj2._meta.app_label == 'user':
            return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'user':
            return db == 'user'
        return None

