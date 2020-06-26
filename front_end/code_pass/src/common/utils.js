import {getRequest} from '../network/api'
import {Message} from 'element-ui'

export const isNotNullORBlank = (...args)=> {
  for (var i = 0; i < args.length; i++) {
    var argument = args[i];

    if (argument == null || argument === '' || argument === "undefined") {
      // Message.warning({message: '数据不能为空!'})
      return false;
    }
  }
  return true;
};
export function FormatDate(date, fmt) {
    date = new Date(date);
    if (typeof(fmt) === "undefined") {
        fmt = "yyyy-MM-dd hh:mm:ss";
    }
    if (/(y+)/.test(fmt)) {
        fmt = fmt.replace(RegExp.$1, (date.getFullYear() + '').substr(4 - RegExp.$1.length))
    }
    let o = {
        'M+': date.getMonth() + 1,
        'd+': date.getDate(),
        'h+': date.getHours(),
        'm+': date.getMinutes(),
        's+': date.getSeconds()
    };
    for (let k in o) {
        if (new RegExp(`(${k})`).test(fmt)) {
            let str = o[k] + '';
            fmt = fmt.replace(RegExp.$1, RegExp.$1.length === 1 ? str : ('00' + str).substr(str.length));
        }
    }
    return fmt
}
export const initMenu = (router, store)=> {
  if (store.state.routes && store.state.routes.length > 0) {
    return;
  }
  getRequest("/menus_info/?user_id="+store.state.currentHr.id+"&"+"identity="+store.state.currentHr.identity).then(resp => {
    console.log('------------菜单数据------------');
    console.log(resp.data.data);
    if (resp) {

      let fmtRoutes = formatRoutes(resp.data.data);
      console.log(fmtRoutes);

      router.addRoutes(fmtRoutes);
      store.commit('init_routes', fmtRoutes);
      // store.dispatch('connect');
    }
  })
};

export const formatRoutes = (routes) => {
    let fmRoutes = [];
    routes.forEach(router => {
        let {
            path,
            component,
            name,
            iconCls,
            keepAlive,
            requireAuth,
            children
        } = router;

        if (children && children instanceof Array) {
            children = formatRoutes(children);
        }
        let fmRouter = {
            path: path,
            name: name,
            iconCls: iconCls,
            meta: {keepAlive:keepAlive,requireAuth:requireAuth},
            children: children,
            component(resolve) {
                if (component.startsWith("Home")) {
                    require(['../views/' + component + '.vue'], resolve);
                } else if (component.startsWith("teacher")) {
                    require(['../views/admin/teacher/' + component + '.vue'], resolve);
                } else if (component.startsWith("detect")) {
                    require(['../views/admin/codedetection/' + component + '.vue'], resolve);
                } else if (component.startsWith("report")) {
                    require(['../views/admin/report/' + component + '.vue'], resolve);
                } else if (component.startsWith("auth")) {
                    require(['../views/admin/authority/' + component + '.vue'], resolve);
                }
            }
        };
        fmRoutes.push(fmRouter);
    });
    return fmRoutes;
};
