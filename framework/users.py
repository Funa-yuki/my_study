#UsersがcheckUserに機能を移譲する

class User(object):
    def __init__(self, ip_addr, **option):
        self.ip_addr = ip_addr
        self.locals = {}
        #self.locals = {func_nane: localargs, ...}
    def addLocals(self, func_name, localargs):
        local_dict = {
            func_name: localargs,
        }
        self.locals.update(local_dict)

class Users(object):
    def __init__(self):
        pass
        self.user_list = []

    def exist_user(self, ip_addr):
        for user in self.user_list:
            if user.ip_addr == ip_addr:
                return user
        return None

    def create_user(self, ip_addr):
        user = User(ip_addr)
        return user

    def userUpdate(self, user, route_func_name, localargs):
        user.addLocals(route_func_name, localargs)
        return user

    def usersUpdate(self, ip_addr, route_func_name, localargs):
        user = self.exist_user(ip_addr)
        if user == None:
            user = self.create_user(ip_addr)
            user = self.userUpdate(user, route_func_name, localargs)
            self.user_list.append(user)
            return user

        updated_user = self.userUpdate(user, route_func_name, localargs)
        for i, user_instance in enumerate(self.user_list):
            if user_instance.ip_addr == ip_addr:
                self.user_list[i] = updated_user
        return updated_user

def route1(a):
    b = a
    return locals()

if __name__=="__main__":
    # check関数部分のテストコード
    ip_addr = '127.0.0.1'
    ip_addr2 = '127.0.0.2'

    users = Users()
    localargs = route1(1)
    user = users.usersUpdate(ip_addr, 'route1', localargs)
    for user in users.user_list:
        print(user.ip_addr, end=", ")
        print(user.locals)
    print()

    localargs = route1(2)
    user = users.usersUpdate(ip_addr, 'route2', localargs)
    for user in users.user_list:
        print(user.ip_addr, end=", ")
        print(user.locals)
    print()

    localargs = route1(3)
    user = users.usersUpdate(ip_addr2, 'route2', localargs)
    for user in users.user_list:
        print(user.ip_addr, end=", ")
        print(user.locals)
    print()

    localargs = route1(4)
    user = users.usersUpdate(ip_addr2, 'route2', localargs)
    for user in users.user_list:
        print(user.ip_addr, end=", ")
        print(user.locals)

        # func1のlocalargsとfunc2のlocalargsが一緒くたになってる
