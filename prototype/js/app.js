/* 路由与初始化 */
(function (global) {
  'use strict';

  var routes = {
    login: { view: 'renderLogin', auth: false },
    register: { view: 'renderRegister', auth: false },
    projects: { view: 'renderProjects', auth: true },
    settings: { view: 'renderSettings', auth: true },
    admin: { view: 'renderAdmin', auth: true, adminOnly: true },
    project: { view: null, auth: true }, // 由 params.view 决定
    'create-project': { view: 'renderNewProject', auth: true }
  };

  function parseHash() {
    var hash = location.hash.replace(/^#\/?/, '');
    var path = hash.split('?')[0];
    var query = {};
    (hash.split('?')[1] || '').split('&').forEach(function (kv) {
      var p = kv.split('=');
      if (p[0]) query[decodeURIComponent(p[0])] = decodeURIComponent(p[1] || '');
    });
    var seg = path.split('/').filter(Boolean); // e.g. ['project','p1','home']
    var route = { name: seg[0] || 'login', params: {}, query: query };

    if (route.name === 'project' && seg[1]) {
      route.params.projectId = seg[1];
      route.params.view = seg[2] || 'home';
    }
    return route;
  }

  function requireAuth(route) {
    var def = routes[route.name];
    var needAuth = def ? def.auth !== false : true;
    if (!needAuth) return true; // login / register 等公开路由
    if (!ST.state.currentUser) {
      location.hash = '#/login';
      return false;
    }
    if (route.name === 'admin') {
      var u = ST.findUser(ST.state.currentUser);
      if (!u || !u.admin) {
        location.hash = '#/projects';
        UI.toast('无权限访问 admin 后台', 'fail');
        return false;
      }
    }
    return true;
  }

  function viewFor(route) {
    if (route.name === 'project') {
      var map = { home: 'renderHome', build: 'renderBuild', cases: 'renderCases', run: 'renderRun', reports: 'renderReports', model: 'renderModel', debug: 'renderDebug' };
      return map[route.params.view] || 'renderHome';
    }
    return (routes[route.name] || routes.login).view;
  }

  function render() {
    var route = parseHash();
    App.route = route;

    if (!requireAuth(route)) return;

    var viewName = viewFor(route);
    if (viewName && Views[viewName]) Views[viewName]();
  }

  function setSidebar(html) {
    document.getElementById('sidebar').innerHTML = html;
  }
  function setTopbar(html) {
    document.getElementById('topbar').innerHTML = html;
  }

  global.App = {
    route: parseHash(), render: render, setSidebar: setSidebar, setTopbar: setTopbar
  };

  window.addEventListener('hashchange', render);

  // 启动
  if (!location.hash) location.hash = '#/login';
  render();
})(window);
