/* 视图渲染 */
(function (global) {
  'use strict';

  var esc = UI.esc;

  function currentProject() {
    var id = App.route.params.projectId;
    return ST.findProject(id);
  }

  /* ============ 登录 ============ */
  function renderLogin() {
    App.setSidebar('');
    App.setTopbar('');
    document.getElementById('view').innerHTML =
      '<div class="auth-bg"><div class="auth-glow g1"></div><div class="auth-glow g2"></div>' +
        '<div class="auth-glass">' +
          '<div class="auth-left">' +
            '<div class="brand-row"><div class="logo">◈</div><span>Web 端智能测试系统</span></div>' +
            '<h1 class="grad-text">让测试<br/>自动发生</h1>' +
            '<p class="auth-sub">只需 URL 与测试账号，自动完成探索、建模、测试与报告</p>' +
            '<ul class="feat">' +
              '<li><span class="fi">◈</span><div><b>AI 自主探索</b><em>遍历站点，生成功能图与接口清单</em></div></li>' +
              '<li><span class="fi">⇄</span><div><b>四类测试全覆盖</b><em>功能 · 接口 · 性能 · 网站机制</em></div></li>' +
              '<li><span class="fi">⇉</span><div><b>多账号交叉压测</b><em>分摊并发，降低单账号风险</em></div></li>' +
            '</ul>' +
            '<div class="auth-meta">需求原型 v1.1 · 仅交互设计 · 无后端逻辑</div>' +
          '</div>' +
          '<div class="auth-right">' +
            '<h2>欢迎回来</h2>' +
            '<p class="auth-hint">使用邮箱登录你的工作台</p>' +
            '<div class="field"><label>邮箱</label><input class="input" id="login-email" value="dev@example.com" /></div>' +
            '<div class="field"><label>密码</label><input class="input" type="password" id="login-pass" value="password" /></div>' +
            '<button class="btn btn-primary btn-block btn-lg" onclick="Views.doLogin()">登 录</button>' +
            '<div class="auth-links"><a href="#/register">注册账号 →</a><a href="#" onclick="Views.forgot();return false;">忘记密码</a></div>' +
            '<div class="auth-demo"><div class="lbl">演示快捷入口</div>' +
              '<button class="btn btn-ghost btn-sm" onclick="Views.quickLogin(\'u1\')">以「林小满」进入</button>' +
              '<button class="btn btn-ghost btn-sm" onclick="Views.quickLogin(\'admin\')">以「平台管理员」进入</button>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>';
  }

  function renderRegister() {
    App.setSidebar(''); App.setTopbar('');
    document.getElementById('view').innerHTML =
      '<div class="auth-bg"><div class="auth-glow g1"></div><div class="auth-glow g2"></div>' +
        '<div class="auth-glass narrow">' +
          '<div class="auth-left">' +
            '<div class="brand-row"><div class="logo">◈</div><span>Web 端智能测试系统</span></div>' +
            '<h1 class="grad-text">创建账号</h1>' +
            '<p class="auth-sub">仅支持邮箱注册，注册时验证邮箱</p>' +
            '<ul class="feat">' +
              '<li><span class="fi">◈</span><div><b>零门槛闭环</b><em>探索 → 建模 → 测试 → 报告</em></div></li>' +
            '</ul>' +
            '<div class="auth-meta">注册即表示同意平台免责声明</div>' +
          '</div>' +
          '<div class="auth-right">' +
            '<h2>注册账号</h2>' +
            '<p class="auth-hint">填写邮箱并完成验证</p>' +
            '<div class="field"><label>邮箱 <span class="req">*</span></label><input class="input" id="reg-email" placeholder="you@example.com" /></div>' +
            '<div class="field"><label>验证码 <span class="req">*</span></label>' +
              '<div class="form-row"><input class="input" placeholder="邮箱验证码" /><button class="btn btn-ghost" style="flex:0 0 auto">发送验证码</button></div></div>' +
            '<div class="field"><label>密码 <span class="req">*</span></label><input class="input" type="password" placeholder="设置密码" /></div>' +
            '<div class="field"><label class="checkbox-label"><input type="checkbox" checked /> 我已阅读并同意平台<a href="#" onclick="Views.disclaimer();return false;">免责声明</a></label></div>' +
            '<button class="btn btn-primary btn-block btn-lg" onclick="Views.registerDone()">注 册</button>' +
            '<div class="auth-links"><a href="#/login">← 返回登录</a></div>' +
          '</div>' +
        '</div>' +
      '</div>';
  }

  function disclaimer() {
    UI.openModal(UI.modal('平台免责声明', '<div class="card" style="box-shadow:none"><div class="card-b" style="font-size:13.5px;color:var(--text-2);line-height:1.9">' + esc(ST.state.platform.disclaimer) + '</div></div>', '<button class="btn btn-primary" onclick="UI.closeModal()">我知道了</button>'));
  }

  function forgot() { UI.toast('原型演示：找回密码流程省略', 'fail'); }

  function doLogin() {
    var email = document.getElementById('login-email').value.trim();
    var u = ST.state.users.find(function (x) { return x.email === email; });
    if (!u) { UI.toast('账号不存在，请使用演示账号', 'fail'); return; }
    quickLogin(u.id);
  }

  function quickLogin(userId) {
    ST.state.currentUser = userId;
    ST.persist();
    UI.toast('已登录：' + ST.findUser(userId).name, 'ok');
    location.hash = '#/projects';
  }

  function registerDone() {
    UI.toast('原型演示：注册后需邮箱验证，此处直接返回登录', 'ok');
    location.hash = '#/login';
  }

  /* ============ 平台首页 ============ */
  function renderProjects() {
    App.setSidebar(sidebarHtml('home'));
    App.setTopbar('<div class="crumb">平台首页</div><div class="right">' + userChip() + '</div>');
    document.getElementById('view').innerHTML =
      '<div class="hero">' +
        '<div class="hero-badge">AI 驱动 · 全流程自动化</div>' +
        '<h1>开始你的第一次智能测试</h1>' +
        '<p>只需提供被测网站 URL 与测试账号，系统自动完成探索、建模、测试与报告。项目创建后可在左侧项目列表中管理。</p>' +
        '<button class="btn btn-lg" onclick="location.hash=\'#/create-project\'">＋ 创建项目</button>' +
        '<div class="hero-steps">' +
          '<div class="hstep"><span class="n">1</span>创建项目（URL + 测试账号）</div>' +
          '<span class="harrow">→</span>' +
          '<div class="hstep"><span class="n">2</span>绑定模型配置</div>' +
          '<span class="harrow">→</span>' +
          '<div class="hstep"><span class="n">3</span>自动探索并生成测试</div>' +
        '</div>' +
      '</div>' +
      '<div class="muted" style="margin:22px 0 12px;font-size:13px;font-weight:600">平台测试能力</div>' +
      '<div class="grid grid-3">' + capCards() + '</div>';
  }

  function capCards() {
    var caps = [
      ['ic1', '◉', '功能测试 · UI 自动化', '多级模块用例、脚本回放 + Agent 修复、每步截图留证'],
      ['ic2', '⇄', '接口测试', '正常用例 + 参数 / 安全变异，断言生成后由代码执行'],
      ['ic3', '⚡', '性能测试', '页面加载三场景 + 接口压测，趋势曲线可追溯'],
      ['ic4', '◈', '网站机制测试', 'SEO、分享卡片、推广落地页、服务端直出'],
      ['ic5', '⇉', '多账号交叉压测', '多个测试账号分摊并发，降低单账号风险'],
      ['ic6', '▤', '智能报告', '结论先行，评分与风险等级按固定规则计算']
    ];
    return caps.map(function (c) {
      return '<div class="card cap"><div class="ico ' + c[0] + '">' + c[1] + '</div>' +
        '<div class="cap-body"><h3>' + c[2] + '</h3><p>' + c[3] + '</p></div></div>';
    }).join('');
  }

  /* ============ 创建项目向导 ============ */
  function renderNewProject() {
    App.setSidebar(sidebarHtml('home'));
    App.setTopbar('<div class="crumb"><a href="#/projects">平台首页</a> / <b>创建项目</b></div><div class="right">' + userChip() + '</div>');
    var v = document.getElementById('view');
    v.innerHTML =
      '<div class="card" style="max-width:760px;margin:0 auto">' +
        '<div class="card-h"><div class="t">创建项目 · 第 1 步 / 共 2 步</div><div class="badge badge-info">向导</div></div>' +
        '<div class="card-b">' +
          '<div class="field"><label>项目名称 <span class="req">*</span></label><input class="input" id="np-name" placeholder="如：云上商城" /></div>' +
          '<div class="field"><label>被测网站 URL <span class="req">*</span></label><input class="input" id="np-url" placeholder="https://example.com" />' +
            '<div class="hint">提交前会检测 URL 是否可访问；创建后 URL 不可修改</div></div>' +
          '<div class="divider"></div>' +
          '<div class="muted" style="margin-bottom:10px;font-weight:600;color:var(--text)">测试账号 <span class="tag" style="margin-left:6px">可录入多个 · 至少 1 个</span></div>' +
          '<div id="np-accounts"></div>' +
          '<button class="btn btn-ghost btn-sm" onclick="Views.addAccountRow()">＋ 添加测试账号</button>' +
          '<div class="hint">多账号用于接口压测时交叉使用，降低单个账号的并发风险</div>' +
        '</div>' +
        '<div class="form-foot">' +
          '<button class="btn btn-ghost" onclick="location.hash=\'#/projects\'">取消</button>' +
          '<button class="btn btn-primary" onclick="Views.newProjectNext()">下一步：配置模型</button>' +
        '</div>' +
      '</div>';
    addAccountRow(true);
    addAccountRow(false);
  }

  function accountRowHtml(main) {
    return '<div class="form-row" style="margin-bottom:10px;align-items:flex-end">' +
      '<div class="field" style="margin:0;flex:1"><label style="font-size:12px">' + (main ? '主账号用户名' : '账号用户名') + '</label>' +
        '<input class="input" placeholder="username" /></div>' +
      '<div class="field" style="margin:0;flex:1"><label style="font-size:12px">密码</label><input class="input" type="password" placeholder="••••" /></div>' +
      (main ? '<span class="badge badge-brand" style="margin-bottom:8px">主账号</span>'
            : '<button class="btn btn-ghost btn-sm" style="margin-bottom:4px" onclick="this.parentNode.remove()">删除</button>') +
      '</div>';
  }

  function addAccountRow(main) {
    var box = document.getElementById('np-accounts');
    var div = document.createElement('div');
    div.innerHTML = accountRowHtml(main);
    box.appendChild(div.firstElementChild);
  }

  function newProjectNext() {
    var name = document.getElementById('np-name').value.trim();
    var url = document.getElementById('np-url').value.trim();
    if (!name || !url) { UI.toast('请填写项目名称和 URL', 'fail'); return; }
    var p = {
      id: ST.uid('p'), name: name, url: url, creator: ST.state.currentUser,
      status: 'empty', planIncomplete: false, version: 0,
      accounts: [{ id: ST.uid('a'), user: 'main_user', pass: '••••', main: true, login: 'unused', lastLogin: '—' }],
      model: null, activeDiscovery: true, perAccountLimit: ST.state.platform.perAccountLimit,
      explored: { pages: 0, funcs: 0, apis: 0, minutes: 0, html: false, js: false, network: false }
    };
    ST.state.projects.unshift(p);
    ST.persist();
    App.route.params.projectId = p.id;
    location.hash = '#/project/' + p.id + '/model';
  }

  /* ============ 模型配置 ============ */
  function renderModel() {
    var p = currentProject();
    App.setSidebar(sidebarHtml('project', p));
    App.setTopbar('<div class="crumb"><a href="#/projects">平台首页</a> / <a href="#/project/' + p.id + '/home">' + esc(p.name) + '</a> / <b>模型配置</b></div><div class="right">' + userChip() + '</div>');
    var cfgs = ST.state.modelConfigs;
    var v = document.getElementById('view');
    v.innerHTML =
      '<div class="card" style="max-width:760px;margin:0 auto">' +
        '<div class="card-h"><div class="t">配置模型 · 第 2 步 / 共 2 步</div></div>' +
        '<div class="card-b">' +
          '<div class="field"><label>选择模型配置</label><select class="select" id="np-model">' +
            cfgs.map(function (m) {
              return '<option value="' + m.id + '"' + (m.ok ? '' : ' disabled') + '>' + esc(m.name) + '（' + esc(m.baseUrl) + '）' + (m.ok ? '' : ' · 检测未通过') + '</option>';
            }).join('') +
          '</select><div class="hint">默认加载最近新增的可用配置；也可新增一条配置</div></div>' +
          '<div class="divider"></div>' +
          '<div class="field"><label>或新增模型配置</label></div>' +
          '<div class="field"><label>模型名称</label><input class="input" placeholder="gpt-4o-mini" /></div>' +
          '<div class="field"><label>Base URL</label><input class="input" placeholder="https://api.openai.com/v1" /></div>' +
          '<div class="field"><label>API Key</label><input class="input" type="password" placeholder="sk-••••" /></div>' +
          '<button class="btn btn-ghost btn-sm" onclick="Views.testModel()">测试连通性与图片识别能力</button>' +
          '<div class="hint">模型必须支持图片识别，否则无法保存（用于验证码识别与页面判定）</div>' +
        '</div>' +
        '<div class="form-foot">' +
          '<button class="btn btn-ghost" onclick="Views.skipModel()">跳过（保留空项目）</button>' +
          '<button class="btn btn-primary" onclick="Views.finishModel()">完成创建</button>' +
        '</div>' +
      '</div>';
  }

  function testModel() {
    UI.openModal(UI.modal('模型检测', '<div class="empty"><div class="big">🔌</div><div>正在检测连通性与图片识别能力…</div></div>', '<button class="btn btn-primary" onclick="UI.closeModal();UI.toast(\'检测通过：连通正常，支持图片识别\',\'ok\')">模拟通过</button>'));
  }

  function skipModel() {
    UI.toast('已跳过模型配置，项目保留为空项目', 'ok');
    location.hash = '#/project/' + currentProject().id + '/home';
  }

  function finishModel() {
    var p = currentProject();
    p.model = document.getElementById('np-model').value;
    ST.persist();
    UI.openModal(UI.modal('项目创建成功',
      '<div style="display:flex;gap:14px;align-items:center">' +
        '<div class="ico" style="width:46px;height:46px;border-radius:12px;background:var(--ok-soft);color:var(--ok);display:grid;place-items:center;font-size:22px">✓</div>' +
        '<div>模型已绑定（' + esc((ST.state.modelConfigs.find(function (m) { return m.id === p.model; }) || {}).name || '') + '）<br/><span class="muted" style="font-size:12.5px">是否立即启动方案建设？</span></div>' +
      '</div>',
      '<button class="btn btn-ghost" onclick="UI.closeModal();location.hash=\'#/project/' + p.id + '/home\'">稍后</button>' +
      '<button class="btn btn-primary" onclick="UI.closeModal();Views.startBuild()">开始方案建设</button>'));
  }

  /* ============ 项目首页 ============ */
  function renderHome() {
    var p = currentProject();
    App.setSidebar(sidebarHtml('project', p));
    App.setTopbar('<div class="crumb"><a href="#/projects">平台首页</a> / <b>' + esc(p.name) + '</b></div>' +
      '<div class="right"><button class="btn btn-ghost" onclick="Views.projectSettings()">项目设置</button>' + userChip() + '</div>');

    if (p.status === 'empty') {
      document.getElementById('view').innerHTML =
        '<div class="card empty"><div class="big">🧪</div><h3>' + esc(p.name) + '</h3>' +
        '<p class="muted">空项目：尚未绑定模型或未开始方案建设</p>' +
        '<div style="margin-top:16px;display:flex;gap:10px;justify-content:center">' +
          '<a class="btn btn-soft" href="#/project/' + p.id + '/model">绑定模型</a>' +
          '<button class="btn btn-primary" onclick="Views.startBuild()">开始方案建设</button>' +
        '</div></div>';
      return;
    }

    var cnt = { pass: 38, fail: 3, blocked: 2, none: 4 };
    var running = ST.state.executions.find(function (e) { return e.status === 'running' && e.project === p.id; });
    var issues = ST.state.issues;
    var v = document.getElementById('view');
    v.innerHTML =
      '<div class="grid grid-4">' +
        statCard('✅', 'var(--ok)', cnt.pass, '通过', 'var(--ok)') +
        statCard('❌', 'var(--fail)', cnt.fail, '不通过', 'var(--fail)') +
        statCard('⛔', 'var(--blocked)', cnt.blocked, '阻塞', 'var(--blocked)') +
        statCard('—', 'var(--none)', cnt.none, '未执行', 'var(--none)') +
      '</div>' +
      (running ? '<div class="card" style="margin-top:16px"><div class="card-b">' +
          '<div style="display:flex;align-items:center;gap:12px">' +
            '<span class="dot-live"></span><b>' + esc(running.name) + '</b>' +
            '<span class="badge badge-brand">执行中</span>' +
            '<div class="grow" style="flex:1">' + UI.progressBar(running.progress) + '</div>' +
            '<span class="muted">' + running.progress + '%</span>' +
            '<a class="btn btn-sm btn-ghost" href="#/project/' + p.id + '/run">查看</a>' +
          '</div></div></div>' : '') +
      '<div class="grid grid-2" style="margin-top:16px">' +
        '<div class="card"><div class="card-h"><div class="t">测试项概况</div><a href="#/project/' + p.id + '/cases">全部用例 →</a></div>' +
          '<div class="card-b flush">' + testTypeList(p) + '</div></div>' +
        '<div class="card"><div class="card-h"><div class="t">主动发现的问题</div><a href="#/project/' + p.id + '/reports">查看报告 →</a></div>' +
          '<div class="card-b flush">' + issueList(issues) + '</div></div>' +
      '</div>' +
      '<div class="card" style="margin-top:16px"><div class="card-h"><div class="t">快捷操作</div></div>' +
        '<div class="card-b" style="display:flex;gap:10px;flex-wrap:wrap">' +
          '<button class="btn btn-primary" onclick="Views.startRun()">▶ 全量测试</button>' +
          '<button class="btn btn-ghost" onclick="Views.startRun(\'接口压测\')">接口压测（多账号交叉）</button>' +
          '<button class="btn btn-ghost" onclick="location.hash=\'#/project/' + p.id + '/build\'">重新探索</button>' +
          '<button class="btn btn-ghost" onclick="location.hash=\'#/project/' + p.id + '/reports\'">生成报告</button>' +
        '</div></div>';
  }

  function statCard(emoji, color, num, lbl, textColor) {
    return '<div class="card stat"><div class="ico" style="background:' + color + '22;color:' + color + '">' + emoji + '</div>' +
      '<div><div class="num" style="color:' + textColor + '">' + num + '</div><div class="lbl">' + lbl + '</div></div></div>';
  }

  function testTypeList(p) {
    var types = [
      { n: '功能测试（UI 自动化）', pass: 9, total: 12, href: 'cases&tab=func' },
      { n: '接口测试', pass: 8, total: 10, href: 'cases&tab=api' },
      { n: '页面加载性能', pass: 5, total: 6, href: 'cases&tab=perf' },
      { n: '接口压测', pass: 1, total: 4, href: 'cases&tab=perf' },
      { n: '网站机制测试', pass: 3, total: 4, href: 'cases&tab=mech' }
    ];
    return types.map(function (t) {
      return '<div class="list-item"><div class="grow"><div class="title" style="font-size:13.5px">' + t.n + '</div></div>' +
        '<span class="badge badge-ok">' + t.pass + '</span><span class="muted">/ ' + t.total + '</span>' +
        '<a class="btn btn-ghost btn-sm" href="#/project/' + p.id + '/cases?tab=' + t.href.split('=')[1] + '">运行</a></div>';
    }).join('');
  }

  function issueList(issues) {
    var html = issues.map(function (i) {
      var b = i.severity === '严重' ? 'badge-fail' : i.severity === '一般' ? 'badge-blocked' : 'badge-info';
      return '<div class="list-item"><div class="grow"><div class="title" style="font-size:13px">' + esc(i.desc) +
        (i.status === '误报' ? ' <span class="tag">误报</span>' : '') + '</div>' +
        '<div class="sub">' + esc(i.page) + ' · ' + i.time + '</div></div>' +
        '<span class="badge ' + b + '">' + i.severity + '</span></div>';
    }).join('');
    return html || '<div class="empty" style="padding:28px">暂无问题</div>';
  }

  function projectSettings() {
    var p = currentProject();
    var accs = p.accounts.map(function (a, i) {
      return '<div class="list-item"><div class="grow"><div class="title">' + esc(a.user) +
        (a.main ? ' <span class="badge badge-brand">主账号</span>' : '') + '</div>' +
        '<div class="sub">' + (a.login === 'ok' ? '最近登录 ' + a.lastLogin : a.login === 'fail' ? '登录失败：' + a.failReason : '未使用') + '</div></div>' +
        '<button class="btn btn-ghost btn-sm" onclick="UI.toast(\'原型：编辑账号\')">编辑</button>' +
        (a.main ? '' : '<button class="btn btn-ghost btn-sm" onclick="Views.delAccount(\'' + a.id + '\')">删除</button>') +
        '</div>';
    }).join('');
    UI.openModal(UI.modal('项目设置 · ' + p.name,
      '<div class="field"><label>项目名称</label><input class="input" value="' + esc(p.name) + '" /></div>' +
      '<div class="field"><label>URL（不可修改）</label><input class="input" value="' + esc(p.url) + '" disabled /></div>' +
      '<div class="field"><label>模型配置</label><select class="select">' + ST.state.modelConfigs.map(function (m) { return '<option' + (m.id === p.model ? ' selected' : '') + '>' + esc(m.name) + '</option>'; }).join('') + '</select></div>' +
      '<div class="field"><label>主动发现（页面跳转智能判定）</label>' +
        '<label class="checkbox-label"><input type="checkbox" ' + (p.activeDiscovery ? 'checked' : '') + ' /> 开启（默认开启）</label></div>' +
      '<div class="divider"></div><div style="font-weight:600;margin-bottom:8px">测试账号（' + p.accounts.length + ' 个）</div>' + accs +
      '<button class="btn btn-ghost btn-sm" style="margin-top:8px" onclick="UI.toast(\'原型：新增账号\')">＋ 添加测试账号</button>',
      '<button class="btn btn-ghost" onclick="UI.closeModal()">取消</button><button class="btn btn-primary" onclick="UI.closeModal();UI.toast(\'已保存\',\'ok\')">保存</button>', 640));
  }

  function delAccount(id) {
    var p = currentProject();
    p.accounts = p.accounts.filter(function (a) { return a.id !== id; });
    ST.persist();
    UI.closeModal();
    UI.toast('已删除账号', 'ok');
  }

  /* ============ 方案建设 ============ */
  function renderBuild() {
    var p = currentProject();
    App.setSidebar(sidebarHtml('project', p));
    App.setTopbar('<div class="crumb"><a href="#/projects">平台首页</a> / <a href="#/project/' + p.id + '/home">' + esc(p.name) + '</a> / <b>方案建设</b></div><div class="right">' + userChip() + '</div>');

    var stages = [
      { n: '登录', pct: 100, state: 'done' },
      { n: '探索', pct: p.status === 'building' ? 46 : 100, state: p.status === 'building' ? 'active' : 'done' },
      { n: '产品分析', pct: p.status === 'building' ? 0 : 100, state: p.status === 'building' ? 'todo' : 'done' },
      { n: '用例生成', pct: 0, state: 'todo' },
      { n: '版本发布', pct: 0, state: 'todo' }
    ];
    var overall = p.status === 'building' ? 31 : 100;
    var v = document.getElementById('view');
    v.innerHTML =
      '<div class="card" style="max-width:860px;margin:0 auto">' +
        '<div class="card-h"><div class="t">方案建设进度' + (p.status === 'building' ? ' <span class="dot-live"></span>' : '') + '</div>' +
        (p.status === 'building' ? '<button class="btn btn-danger btn-sm" onclick="Views.stopBuild()">终止</button>' :
          '<button class="btn btn-primary btn-sm" onclick="Views.startBuild()">重新探索</button>') + '</div>' +
        '<div class="card-b">' +
          '<div class="steps" style="margin-bottom:20px">' + stages.map(function (s) {
            var cls = s.state === 'done' ? 'done' : s.state === 'active' ? 'active' : '';
            return '<div class="step ' + cls + '"><div class="dot">' + (s.state === 'done' ? '✓' : (s.state === 'active' ? '•' : '')) + '</div><div class="lbl">' + s.n + '</div><div class="muted" style="font-size:11px">' + (s.state === 'todo' ? '—' : s.pct + '%') + '</div></div>';
          }).join('') + '</div>' +
          '<div class="muted" style="margin-bottom:6px">总进度 ' + overall + '%</div>' +
          UI.progressBar(overall) +
          '<div class="grid grid-2" style="margin-top:20px">' +
            '<div class="card" style="box-shadow:none;border-color:var(--line)"><div class="card-b">' +
              '<div class="muted" style="font-size:12px;margin-bottom:6px">探索实时动态</div>' +
              '<div class="console">' + consoleLines(p) + '</div></div></div>' +
            '<div class="card" style="box-shadow:none;border-color:var(--line)"><div class="card-b">' +
              '<div class="muted" style="font-size:12px;margin-bottom:6px">探索统计</div>' +
              '<div class="kv">' +
                '<div class="k">页面数</div><div>' + p.explored.pages + ' / ' + ST.state.platform.defaultExplorePages + '</div>' +
                '<div class="k">功能模块</div><div>' + p.explored.funcs + '</div>' +
                '<div class="k">接口数</div><div>' + p.explored.apis + '</div>' +
                '<div class="k">已用时长</div><div>' + p.explored.minutes + ' / ' + ST.state.platform.defaultExploreMinutes + ' 分钟</div>' +
                '<div class="k">数据采集</div><div>HTML ✓ · JS ✓ · 网络请求 ✓</div>' +
              '</div></div></div>' +
          '</div>' +
          '<div class="divider"></div>' +
          '<div class="muted" style="font-size:12.5px">方案建设只做探索与用例生成，不执行测试；用例生成完成后才开放测试执行入口。探索上限：' +
            ST.state.platform.defaultExploreMinutes + ' 分钟 / ' + ST.state.platform.defaultExplorePages + ' 页面。</div>' +
        '</div></div>';
  }

  function consoleLines(p) {
    if (p.status === 'building') {
      return '<div class="c-ok">✓ 登录成功（主账号 ' + esc((p.accounts[0] || {}).user || '—') + '）</div>' +
        '<div>· 探索 /goods/list …</div>' +
        '<div>· 探索 /goods/detail/123 …</div>' +
        '<div class="c-warn">· 结构相同页面已合并：/goods/detail/{id}</div>' +
        '<div>· 提交表单：新增收货地址（写接口已采集）</div>' +
        '<div class="c-ok">· 已发现 18 个功能、26 个接口</div>';
    }
    return '<div class="c-ok">✓ 登录成功</div>' +
      '<div class="c-ok">✓ 探索完成：42 页面 / 18 功能 / 26 接口</div>' +
      '<div class="c-ok">✓ 产品分析完成：功能图 / 技术框架图 / 接口清单</div>' +
      '<div class="c-ok">✓ 用例生成完成：功能 12 · 接口 10 · 性能 10 · 机制 4</div>' +
      '<div class="c-ok">✓ 版本 v' + p.version + ' 已发布</div>';
  }

  function startBuild() {
    var p = currentProject();
    p.status = 'building';
    ST.persist();
    UI.toast('方案建设已启动', 'ok');
    location.hash = '#/project/' + p.id + '/build';
  }

  function stopBuild() {
    var p = currentProject();
    p.status = 'ready';
    p.planIncomplete = true;
    ST.persist();
    UI.toast('已终止：用已发现内容生成用例，并标注"探索未完整"', 'ok');
    location.hash = '#/project/' + p.id + '/build';
  }

  /* ============ 用例管理 ============ */
  function renderCases() {
    var p = currentProject();
    App.setSidebar(sidebarHtml('project', p));
    App.setTopbar('<div class="crumb"><a href="#/projects">平台首页</a> / <a href="#/project/' + p.id + '/home">' + esc(p.name) + '</a> / <b>用例管理</b></div><div class="right">' + userChip() + '</div>');

    var tab = (App.route.query.tab || 'func');
    var tabs = [['func', '功能测试'], ['api', '接口测试'], ['perf', '性能测试'], ['mech', '网站机制']];
    var cases = ST.projectCases(p.id).filter(function (c) { return c.type === tab; });

    var v = document.getElementById('view');
    v.innerHTML =
      '<div class="card"><div class="tabs">' + tabs.map(function (t) {
        return '<button class="tab ' + (t[0] === tab ? 'active' : '') + '" onclick="location.hash=\'#/project/' + p.id + '/cases?tab=' + t[0] + '\'">' + t[1] + '</button>';
      }).join('') + '</div>' +
      '<div class="card-b flush">' + caseTable(tab, cases, p) + '</div></div>';
  }

  function caseTable(tab, cases, p) {
    if (!cases.length) { return '<div class="empty"><div class="big">📭</div>当前项目暂无用例，请先完成方案建设</div>'; }
    if (tab === 'func') {
      return '<div class="table-wrap"><table class="tbl"><thead><tr><th>模块 / 用例</th><th>优先级</th><th>结果</th><th>标记</th><th style="width:200px">操作</th></tr></thead><tbody>' +
        cases.map(function (c) {
          return '<tr><td><div style="font-weight:500">' + esc(c.name) + '</div><div class="muted" style="font-size:12px">' + esc(c.module) + ' · ' + esc(c.page) + '</div></td>' +
            '<td>' + UI.pBadge(c.priority) + '</td><td>' + UI.badge(c.result) + '</td>' +
            '<td>' + c.marks.map(function (m) { return '<span class="tag">' + m + '</span>'; }).join(' ') + (c.automatable === 'no' ? '<span class="tag">不可自动化</span>' : '') + '</td>' +
            '<td><button class="btn btn-ghost btn-sm" onclick="Views.caseDetail(\'' + c.id + '\')">详情</button> ' +
            '<button class="btn btn-soft btn-sm" onclick="Views.runCase(\'' + c.id + '\')">运行</button></td></tr>';
        }).join('') + '</tbody></table></div>';
    }
    if (tab === 'api') {
      return '<div class="table-wrap"><table class="tbl"><thead><tr><th>接口</th><th>用例类型</th><th>优先级</th><th>结果</th><th style="width:160px">操作</th></tr></thead><tbody>' +
        cases.map(function (c) {
          return '<tr><td><div class="mono" style="font-weight:500">' + esc(c.apiMethod) + ' ' + esc(c.apiPath) + '</div><div class="muted" style="font-size:12px">' + esc(c.module) + '</div></td>' +
            '<td><span class="tag">' + (c.apiKind === 'normal' ? '正常' : c.apiKind === 'mutation' ? '参数变异' : '安全变异') + '</span></td>' +
            '<td>' + UI.pBadge(c.priority) + '</td><td>' + UI.badge(c.result) + '</td>' +
            '<td><button class="btn btn-ghost btn-sm" onclick="Views.caseDetail(\'' + c.id + '\')">详情</button> ' +
            '<button class="btn btn-soft btn-sm" onclick="Views.runCase(\'' + c.id + '\')">运行</button></td></tr>';
        }).join('') + '</tbody></table></div>';
    }
    if (tab === 'perf') {
      return '<div class="table-wrap"><table class="tbl"><thead><tr><th>性能用例</th><th>场景</th><th>指标</th><th>优先级</th><th>结果</th><th style="width:160px">操作</th></tr></thead><tbody>' +
        cases.map(function (c) {
          return '<tr><td><div style="font-weight:500">' + esc(c.name) + '</div></td>' +
            '<td>' + esc(c.scenario) + '</td><td class="mono muted">' + esc(c.metric) + '</td>' +
            '<td>' + UI.pBadge(c.priority) + '</td><td>' + UI.badge(c.result) + '</td>' +
            '<td><button class="btn btn-ghost btn-sm" onclick="Views.caseDetail(\'' + c.id + '\')">详情</button> ' +
            '<button class="btn btn-soft btn-sm" onclick="Views.runCase(\'' + c.id + '\')">运行</button></td></tr>';
        }).join('') + '</tbody></table></div>';
    }
    return '<div class="table-wrap"><table class="tbl"><thead><tr><th>机制用例</th><th>检查内容</th><th>优先级</th><th>结果</th><th style="width:160px">操作</th></tr></thead><tbody>' +
      cases.map(function (c) {
        return '<tr><td><div style="font-weight:500">' + esc(c.name) + '</div></td>' +
          '<td class="muted">' + esc(c.steps) + '</td><td>' + UI.pBadge(c.priority) + '</td><td>' + UI.badge(c.result) + '</td>' +
          '<td><button class="btn btn-ghost btn-sm" onclick="Views.caseDetail(\'' + c.id + '\')">详情</button> ' +
          '<button class="btn btn-soft btn-sm" onclick="Views.runCase(\'' + c.id + '\')">运行</button></td></tr>';
      }).join('') + '</tbody></table></div>';
  }

  function caseDetail(id) {
    var c = ST.state.cases.find(function (x) { return x.id === id; });
    UI.openModal(UI.modal('用例详情 · ' + c.name,
      '<div class="kv">' +
        '<div class="k">优先级</div><div>' + UI.pBadge(c.priority) + '</div>' +
        '<div class="k">当前结果</div><div>' + UI.badge(c.result) + '</div>' +
        '<div class="k">是否自动化</div><div>' + (c.automatable === 'yes' ? '是' : '否') + '</div>' +
        '<div class="k">前置条件</div><div>数据准备完成，可独立执行</div>' +
      '</div>' +
      '<div class="divider"></div>' +
      '<div class="field"><label>执行步骤（可编辑，编辑后重新生成脚本）</label><textarea class="textarea">' + esc(c.steps) + '</textarea></div>' +
      '<div class="field"><label>预期结果</label><textarea class="textarea">' + esc(c.expect) + '</textarea></div>',
      '<button class="btn btn-ghost" onclick="UI.closeModal()">取消</button>' +
      '<button class="btn btn-ghost" onclick="UI.closeModal();location.hash=\'#/project/' + App.route.params.projectId + '/debug?case=' + c.id + '\'">调试执行</button>' +
      '<button class="btn btn-primary" onclick="UI.closeModal();UI.toast(\'已保存，标记「人工修改」\',\'ok\')">保存</button>', 620));
  }

  function runCase(id) {
    var c = ST.state.cases.find(function (x) { return x.id === id; });
    if (c.automatable === 'no') { UI.toast('该用例不可自动化，执行时跳过，保持未执行', 'fail'); return; }
    UI.toast('已提交执行：' + c.name, 'ok');
    setTimeout(function () {
      c.result = Math.random() > 0.75 ? 'fail' : 'pass';
      ST.persist();
      UI.toast('执行完成：' + c.name + ' → ' + (c.result === 'pass' ? '通过' : '不通过'), c.result === 'pass' ? 'ok' : 'fail');
      App.render();
    }, 900);
  }

  /* ============ 调试执行 ============ */
  function debugResult(c) {
    var pass = c.result !== 'fail';
    var steps = [
      { t: '登录被测网站（使用主账号）', ok: true, shot: true },
      { t: '进入目标页面并加载完成', ok: true, shot: true },
      { t: '执行：' + c.steps, ok: pass, shot: true },
      { t: '断言：' + c.expect, ok: pass, shot: pass }
    ];
    var asserts = [
      { t: '目标元素「' + c.name + '」可正常访问', ok: pass },
      { t: '执行结果与预期结果一致', ok: pass }
    ];
    var consoleErrors = pass ? [] : ['Uncaught TypeError: Cannot read properties of undefined', 'Failed to load resource: 404'];
    var requests = [
      { m: 'GET', p: '/api/' + (c.type === 'api' ? (c.apiPath || 'items') : 'page'), s: 200, d: '86ms' },
      { m: 'POST', p: '/api/action', s: pass ? 200 : 500, d: pass ? '120ms' : '—' }
    ];
    return { steps: steps, asserts: asserts, consoleErrors: consoleErrors, requests: requests, pass: pass };
  }

  function renderDebug() {
    var p = currentProject();
    var cid = App.route.query.case;
    var c = ST.state.cases.find(function (x) { return x.id === cid; });
    if (!c) { UI.toast('用例不存在', 'fail'); location.hash = '#/project/' + p.id + '/cases'; return; }
    App.setSidebar(sidebarHtml('project', p));
    App.setTopbar('<div class="crumb"><a href="#/projects">平台首页</a> / <a href="#/project/' + p.id + '/home">' + esc(p.name) + '</a> / <a href="#/project/' + p.id + '/cases">用例管理</a> / <b>调试执行</b></div><div class="right">' + userChip() + '</div>');
    var r = debugResult(c);
    var steps = r.steps.map(function (s, i) {
      return '<div class="dstep">' +
        '<div class="ds-icon ' + (s.ok ? 'ok' : 'fail') + '">' + (s.ok ? '✓' : '✕') + '</div>' +
        '<div class="ds-body"><div class="ds-t">' + (i + 1) + '. ' + esc(s.t) + '</div>' +
        (s.shot ? '<div class="shot">截图 ' + (i + 1) + '（占位）</div>' : '') +
        '</div></div>';
    }).join('');
    var asserts = r.asserts.map(function (a) {
      return '<div class="list-item"><span class="badge ' + (a.ok ? 'badge-ok' : 'badge-fail') + '">' + (a.ok ? '通过' : '不通过') + '</span><div class="grow">' + esc(a.t) + '</div></div>';
    }).join('');
    var consoleHtml = r.consoleErrors.length
      ? r.consoleErrors.map(function (e) { return '<div class="cline cline-err">' + esc(e) + '</div>'; }).join('')
      : '<div class="cline cline-ok">无控制台错误</div>';
    var reqHtml = r.requests.map(function (q) {
      return '<tr><td class="mono">' + q.m + '</td><td class="mono">' + esc(q.p) + '</td>' +
        '<td>' + (q.s < 400 ? '<span class="badge badge-ok">' + q.s + '</span>' : '<span class="badge badge-fail">' + q.s + '</span>') + '</td>' +
        '<td class="mono">' + q.d + '</td></tr>';
    }).join('');

    document.getElementById('view').innerHTML =
      '<div class="grid grid-2" style="align-items:start">' +
        '<div class="card"><div class="card-h"><div class="t">用例信息</div><a href="#/project/' + p.id + '/cases">返回用例 →</a></div>' +
          '<div class="card-b"><div class="kv">' +
            '<div class="k">用例名称</div><div>' + esc(c.name) + '</div>' +
            '<div class="k">优先级</div><div>' + UI.pBadge(c.priority) + '</div>' +
            '<div class="k">所属模块</div><div>' + esc(c.module) + '</div>' +
            '<div class="k">是否自动化</div><div>' + (c.automatable === 'yes' ? '是' : '否') + '</div>' +
            '<div class="k">预期结果</div><div>' + esc(c.expect) + '</div>' +
          '</div></div></div>' +
        '<div class="card"><div class="card-h"><div class="t">调试结果</div></div>' +
          '<div class="card-b"><div class="kv">' +
            '<div class="k">执行结果</div><div>' + UI.badge(r.pass ? 'pass' : 'fail') + '</div>' +
            '<div class="k">执行耗时</div><div>1.8s</div>' +
            '<div class="k">执行时间</div><div>刚刚（调试执行，不计入历史结果）</div>' +
          '</div></div></div>' +
      '</div>' +
      '<div class="grid grid-2" style="margin-top:16px;align-items:start">' +
        '<div class="card"><div class="card-h"><div class="t">执行步骤</div></div><div class="card-b">' + steps + '</div></div>' +
        '<div class="card"><div class="card-h"><div class="t">断言结果</div></div><div class="card-b flush">' + asserts + '</div></div>' +
      '</div>' +
      '<div class="grid grid-2" style="margin-top:16px;align-items:start">' +
        '<div class="card"><div class="card-h"><div class="t">控制台错误</div></div><div class="card-b"><div class="console">' + consoleHtml + '</div></div></div>' +
        '<div class="card"><div class="card-h"><div class="t">网络请求</div></div><div class="card-b flush"><div class="table-wrap"><table class="tbl"><thead><tr><th>方法</th><th>路径</th><th>状态</th><th>耗时</th></tr></thead><tbody>' + reqHtml + '</tbody></table></div></div></div>' +
      '</div>' +
      '<div class="card" style="margin-top:16px"><div class="card-b" style="display:flex;gap:10px">' +
        '<button class="btn btn-primary" onclick="Views.reRunDebug()">重新调试</button>' +
        '<button class="btn btn-ghost" onclick="location.hash=\'#/project/' + p.id + '/cases\'">返回用例列表</button>' +
      '</div></div>';
  }

  function reRunDebug() {
    UI.toast('重新调试执行完成', 'ok');
    App.render();
  }

  /* ============ 测试执行 ============ */
  function renderRun() {
    var p = currentProject();
    App.setSidebar(sidebarHtml('project', p));
    App.setTopbar('<div class="crumb"><a href="#/projects">平台首页</a> / <a href="#/project/' + p.id + '/home">' + esc(p.name) + '</a> / <b>测试执行</b></div><div class="right">' + userChip() + '</div>');

    var running = ST.state.executions.find(function (e) { return e.status === 'running' && e.project === p.id; });
    var v = document.getElementById('view');
    if (!running) {
      v.innerHTML = '<div class="card empty"><div class="big">▶️</div><h3>启动一次测试执行</h3>' +
        '<p class="muted">同一项目同一时间只运行一个任务，其余任务排队</p>' +
        '<div style="margin-top:16px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">' +
          '<button class="btn btn-primary" onclick="Views.startRun()">全量测试</button>' +
          '<button class="btn btn-ghost" onclick="Views.startRun(\'功能测试\')">功能测试</button>' +
          '<button class="btn btn-ghost" onclick="Views.startRun(\'接口测试\')">接口测试</button>' +
          '<button class="btn btn-ghost" onclick="Views.startRun(\'接口压测\')">接口压测</button>' +
          '<button class="btn btn-ghost" onclick="Views.startRun(\'网站机制\')">网站机制</button>' +
        '</div></div>';
      return;
    }
    var order = running.order;
    v.innerHTML =
      '<div class="grid grid-3">' +
        '<div class="card stat"><div class="ico" style="background:var(--brand-soft);color:var(--brand)">⚡</div><div><div class="num">' + running.progress + '%</div><div class="lbl">执行进度</div></div></div>' +
        '<div class="card stat"><div class="ico" style="background:var(--ok-soft);color:var(--ok)">✅</div><div><div class="num">' + running.summary.pass + '</div><div class="lbl">通过</div></div></div>' +
        '<div class="card stat"><div class="ico" style="background:var(--fail-soft);color:var(--fail)">❌</div><div><div class="num">' + running.summary.fail + '</div><div class="lbl">不通过</div></div></div>' +
      '</div>' +
      '<div class="card" style="margin-top:16px"><div class="card-h"><div class="t">' + esc(running.name) + ' <span class="dot-live"></span></div>' +
        '<button class="btn btn-danger btn-sm" onclick="Views.stopRun()">终止</button></div>' +
        '<div class="card-b"><div class="muted" style="margin-bottom:8px">执行顺序：' + order.map(function (o, i) { return (i === 1 ? '<b style="color:var(--brand)">' + o + '</b>' : o); }).join(' → ') + '</div>' +
          UI.progressBar(running.progress) +
        '</div></div>' +
      (running.accounts ? '<div class="card" style="margin-top:16px"><div class="card-h"><div class="t">多账号交叉压测分配</div></div>' +
        '<div class="card-b flush"><div class="table-wrap"><table class="tbl"><thead><tr><th>账号</th><th>已发请求</th><th>错误率</th><th>状态</th></tr></thead><tbody>' +
        running.accounts.map(function (a) {
          return '<tr><td>' + esc(a.user) + '</td><td>' + (a.req || 0) + '</td><td>' + (a.err == null ? '—' : a.err + '%') + '</td>' +
            '<td>' + (a.skip ? '<span class="badge badge-blocked">跳过：' + esc(a.skip) + '</span>' : '<span class="badge badge-ok">压测中</span>') + '</td></tr>';
        }).join('') + '</tbody></table></div></div></div>' : '');
  }

  function startRun(type) {
    var p = currentProject();
    if (p.status === 'empty') { UI.toast('请先完成方案建设', 'fail'); return; }
    ST.state.executions.forEach(function (e) { if (e.status === 'running' && e.project === p.id) e.status = 'done'; });
    var name = (type || '全量测试');
    var e = {
      id: ST.uid('e'), project: p.id, name: name, status: 'running',
      progress: 0, startedAt: '刚刚', finishedAt: null, version: p.version,
      order: type ? [type] : ['功能', '接口', '页面加载性能', '网站机制', '接口压测'],
      summary: { pass: 0, fail: 0, blocked: 0, none: 0 },
      accounts: (type === '接口压测' ? p.accounts.map(function (a) { return { user: a.user, req: a.main ? 320 : a.login === 'ok' ? 300 : 0, err: a.login === 'ok' ? 0.2 : null, skip: a.login === 'ok' ? null : '登录失败' }; }) : null)
    };
    ST.state.executions.unshift(e);
    ST.persist();
    UI.toast('已启动：' + name, 'ok');
    location.hash = '#/project/' + p.id + '/run';
    if (ST.state._runTimer) clearInterval(ST.state._runTimer);
    ST.state._runTimer = setInterval(function () {
      e.progress += 7;
      e.summary.pass = Math.round(e.progress * 0.6);
      e.summary.fail = e.progress > 40 ? Math.round(e.progress * 0.04) : 0;
      e.summary.blocked = e.progress > 20 ? 1 : 0;
      if (e.progress >= 100) {
        e.progress = 100; e.status = 'done'; e.finishedAt = '刚刚';
        clearInterval(ST.state._runTimer);
        UI.toast(name + ' 完成', 'ok');
      }
      ST.persist();
      if (App.route.name === 'run') App.render();
    }, 700);
  }

  function stopRun() {
    var p = currentProject();
    var e = ST.state.executions.find(function (x) { return x.status === 'running' && x.project === p.id; });
    if (e) { e.status = 'done'; e.finishedAt = '刚刚（已终止）'; }
    if (ST.state._runTimer) clearInterval(ST.state._runTimer);
    ST.persist();
    UI.toast('已终止：已完成用例的结果保留，其余保持未执行', 'ok');
    App.render();
  }

  /* ============ 报告 ============ */
  function renderReports() {
    var p = currentProject();
    App.setSidebar(sidebarHtml('project', p));
    App.setTopbar('<div class="crumb"><a href="#/projects">平台首页</a> / <a href="#/project/' + p.id + '/home">' + esc(p.name) + '</a> / <b>报告</b></div><div class="right">' + userChip() + '</div>');
    var reports = ST.state.reports.filter(function (r) { return r.project === p.id; });
    var v = document.getElementById('view');
    v.innerHTML =
      '<div class="card" style="margin-bottom:16px"><div class="card-b" style="display:flex;align-items:center;gap:14px">' +
        '<div style="flex:1"><b>生成测试报告</b><div class="muted" style="font-size:12.5px">报告与执行分开，由你手动生成；范围可选「某一次执行」或「项目当前状态」</div></div>' +
        '<button class="btn btn-primary" onclick="Views.genReport()">生成报告</button></div></div>' +
      '<div class="grid grid-2">' + reports.map(reportCard).join('') + '</div>' +
      (reports.length ? '' : '<div class="card empty"><div class="big">📄</div>暂无报告</div>');
  }

  function reportCard(r) {
    return '<div class="card"><div class="card-b" style="display:flex;gap:16px">' +
      '<div>' + UI.ring(r.score) + '</div>' +
      '<div class="grow" style="min-width:0">' +
        '<div class="title" style="font-size:15px">' + esc(r.title) + '</div>' +
        '<div class="muted" style="font-size:12.5px;margin:4px 0">范围：' + esc(r.scope) + ' · 方案 v' + r.version + ' · ' + r.time + '</div>' +
        '<div style="margin:8px 0 4px">风险等级：' + UI.riskHtml(r.risk) + '</div>' +
        '<div class="muted" style="font-size:12.5px">主要问题：' + esc(r.top[0]) + (r.top.length > 1 ? ' 等 ' + r.top.length + ' 项' : '') + '</div>' +
        '<div style="margin-top:10px;display:flex;gap:8px">' +
          '<button class="btn btn-soft btn-sm" onclick="Views.reportDetail(\'' + r.id + '\')">查看</button>' +
          '<button class="btn btn-ghost btn-sm" onclick="UI.toast(\'原型：导出 PDF\',\'ok\')">导出 PDF</button>' +
        '</div>' +
      '</div></div></div>';
  }

  function genReport() {
    var p = currentProject();
    var r = {
      id: ST.uid('r'), project: p.id, title: p.name + ' · 测试报告', scope: '项目当前状态',
      score: 82 + Math.floor(Math.random() * 10), risk: '中', time: '刚刚', version: p.version,
      top: ['商品详情规格切换渲染异常（严重）', '无库存时购买按钮未置灰', '优惠券金额精度错误'],
      summary: '本报告基于项目当前状态汇总，统计由代码按固定规则计算，结论摘要由报告摘要 Agent 撰写。'
    };
    ST.state.reports.unshift(r);
    ST.persist();
    UI.toast('报告已生成', 'ok');
    location.hash = '#/project/' + p.id + '/reports';
  }

  function reportDetail(id) {
    var r = ST.state.reports.find(function (x) { return x.id === id; });
    UI.openModal(UI.modal(r.title,
      '<div style="display:flex;gap:16px;align-items:center;margin-bottom:16px">' +
        '<div>' + UI.ring(r.score) + '</div>' +
        '<div><div>风险等级：' + UI.riskHtml(r.risk) + '</div><div class="muted" style="font-size:12.5px">' + esc(r.scope) + '</div></div></div>' +
      '<div class="field"><label>结论摘要</label><div class="card" style="box-shadow:none"><div class="card-b" style="font-size:13.5px;color:var(--text-2)">' + esc(r.summary) + '</div></div></div>' +
      '<div class="field"><label>主要问题</label><ol style="margin:0;padding-left:20px">' + r.top.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ol></div>' +
      '<div class="field"><label>固定内容</label><div class="muted" style="font-size:12.5px">未覆盖说明 · 探索未完整标注 · 方案版本 v' + r.version + '</div></div>',
      '<button class="btn btn-primary" onclick="UI.closeModal();UI.toast(\'原型：导出 PDF\',\'ok\')">导出 PDF</button>', 620));
  }

  /* ============ 设置 ============ */
  function renderSettings() {
    App.setSidebar(sidebarHtml('settings'));
    App.setTopbar('<div class="crumb"><b>设置</b></div><div class="right">' + userChip() + '</div>');
    var pl = ST.state.platform;
    var v = document.getElementById('view');
    v.innerHTML =
      '<div class="grid grid-2" style="max-width:960px">' +
        '<div class="card"><div class="card-h"><div class="t">模型配置（收集表）</div></div><div class="card-b flush">' +
          ST.state.modelConfigs.map(function (m) {
            return '<div class="list-item"><div class="grow"><div class="title">' + esc(m.name) + '</div>' +
              '<div class="sub mono">' + esc(m.baseUrl) + ' · ' + esc(m.key) + '</div></div>' +
              '<span class="badge ' + (m.ok ? 'badge-ok' : 'badge-fail') + '">' + (m.ok ? '检测通过' : '检测未通过') + '</span>' +
              '<button class="btn btn-ghost btn-sm">编辑</button></div>';
          }).join('') +
          '<div class="card-b"><button class="btn btn-ghost btn-sm">＋ 新增模型配置</button></div>' +
        '</div></div>' +
        '<div class="card"><div class="card-h"><div class="t">探索限制</div></div><div class="card-b">' +
          '<div class="field"><label>时长上限（分钟）</label><input class="input" type="number" value="' + pl.defaultExploreMinutes + '" /></div>' +
          '<div class="field"><label>页面数上限</label><input class="input" type="number" value="' + pl.defaultExplorePages + '" /></div>' +
          '<div class="hint">新用户默认取平台设置；结构相同的页面算 1 个</div></div></div>' +
        '<div class="card"><div class="card-h"><div class="t">压测并发</div></div><div class="card-b">' +
          '<div class="field"><label>单接口并发上限</label><input class="input" type="number" value="50" /><div class="hint">不能超过平台全局上限 ' + pl.globalStressLimit + '</div></div>' +
          '<div class="field"><label>单账号并发上限</label><input class="input" type="number" value="' + pl.perAccountLimit + '" /></div>' +
          '<div class="hint">实际并发 = min(单接口上限, 可用账号数 × 单账号上限)</div></div></div>' +
        '<div class="card"><div class="card-h"><div class="t">其他</div></div><div class="card-b" style="display:flex;flex-direction:column;gap:10px">' +
          '<button class="btn btn-ghost" onclick="Views.disclaimer()">查看免责声明</button>' +
          '<button class="btn btn-danger" onclick="Views.resetDemo()">重置演示数据</button>' +
        '</div></div>' +
      '</div>';
  }

  function resetDemo() {
    ST.reset();
    UI.toast('演示数据已重置，请重新登录', 'ok');
    location.hash = '#/login';
  }

  /* ============ admin 后台 ============ */
  function renderAdmin() {
    App.setSidebar(sidebarHtml('admin'));
    App.setTopbar('<div class="crumb"><b>admin 后台</b></div><div class="right">' + userChip() + '</div>');
    var tab = App.route.query.tab || 'users';
    var v = document.getElementById('view');
    var tabs = '<div class="tabs" style="padding:0 0;border:none;margin-bottom:16px">' +
      '<button class="tab ' + (tab === 'users' ? 'active' : '') + '" onclick="location.hash=\'#/admin?tab=users\'">用户管理</button>' +
      '<button class="tab ' + (tab === 'projects' ? 'active' : '') + '" onclick="location.hash=\'#/admin?tab=projects\'">项目管理</button>' +
      '<button class="tab ' + (tab === 'platform' ? 'active' : '') + '" onclick="location.hash=\'#/admin?tab=platform\'">平台设置</button>' +
    '</div>';
    v.innerHTML = tabs + (tab === 'users' ? adminUsers() : tab === 'projects' ? adminProjects() : adminPlatform());
  }

  function adminUsers() {
    return '<div class="card"><div class="card-b flush"><div class="table-wrap"><table class="tbl"><thead><tr><th>用户</th><th>邮箱</th><th>状态</th><th>项目数</th><th style="width:220px">操作</th></tr></thead><tbody>' +
      ST.state.users.map(function (u) {
        var cnt = ST.state.projects.filter(function (p) { return p.creator === u.id; }).length;
        return '<tr><td><div class="title">' + esc(u.name) + (u.admin ? ' <span class="badge badge-brand">admin</span>' : '') + '</div></td>' +
          '<td>' + esc(u.email) + '</td>' +
          '<td>' + (u.status === 'normal' ? '<span class="badge badge-ok">正常</span>' : '<span class="badge badge-blocked">已冻结</span>') + '</td>' +
          '<td>' + cnt + '</td>' +
          '<td>' + (u.admin ? '<span class="muted">内置账号</span>' :
            '<button class="btn btn-ghost btn-sm">重置密码</button> ' +
            (u.status === 'normal' ? '<button class="btn btn-ghost btn-sm">冻结</button>' : '<button class="btn btn-ghost btn-sm">启用</button>') +
            '<button class="btn btn-ghost btn-sm">删除</button>') + '</td></tr>';
      }).join('') + '</tbody></table></div></div></div>';
  }

  function adminProjects() {
    return '<div class="card"><div class="card-b flush">' +
      ST.state.projects.map(function (p) {
        var owner = ST.findUser(p.creator);
        return '<div class="list-item"><div class="grow"><div class="title">' + esc(p.name) + '</div>' +
          '<div class="sub">' + esc(p.url) + ' · 创建者：' + esc(owner ? owner.name : '—') + '</div></div>' +
          UI.statusBadge(p.status) +
          '<button class="btn btn-ghost btn-sm" onclick="Views.deleteProject(\'' + p.id + '\')">删除</button>' +
        '</div>';
      }).join('') + '</div></div>';
  }

  function deleteProject(id) {
    ST.state.projects = ST.state.projects.filter(function (p) { return p.id !== id; });
    ST.persist();
    UI.toast('已删除项目', 'ok');
    App.render();
  }

  function adminPlatform() {
    var pl = ST.state.platform;
    var rows = [
      ['平台总并发任务数', pl.totalConcurrency],
      ['单接口压测全局上限', pl.globalStressLimit],
      ['单账号压测并发默认值', pl.perAccountLimit],
      ['每项目测试账号上限', pl.accountCap],
      ['新用户默认探索时长（分钟）', pl.defaultExploreMinutes],
      ['新用户默认探索页面数', pl.defaultExplorePages],
      ['大文件保留时长（天）', pl.retentionDays],
      ['压测默认持续时长（秒）', pl.stressDuration]
    ];
    return '<div class="card" style="max-width:640px"><div class="card-h"><div class="t">平台设置</div></div><div class="card-b">' +
      rows.map(function (r) {
        return '<div class="field"><label>' + r[0] + '</label><input class="input" type="number" value="' + r[1] + '" /></div>';
      }).join('') +
      '<div class="field"><label>免责声明</label><textarea class="textarea">' + esc(pl.disclaimer) + '</textarea></div>' +
      '<button class="btn btn-primary" onclick="UI.toast(\'已保存平台设置\',\'ok\')">保存</button>' +
    '</div></div>';
  }

  /* ============ 布局 ============ */
  function sidebarHtml(context, project) {
    var me = ST.state.currentUser;
    var user = ST.findUser(me);
    var mine = ST.state.projects.filter(function (p) { return p.creator === me; });
    var html = '<div class="brand"><div class="logo">◈</div>Web 智能测试</div>';
    html += '<div class="nav-label">工作台</div><div class="nav">' +
      navLink('#/projects', '⌂', '平台首页', context === 'home') +
    '</div>';
    html += '<div class="nav-label">项目列表 <span class="cnt">' + mine.length + ' / 10</span></div><div class="proj-list">';
    mine.forEach(function (p) {
      var active = context === 'project' && project && p.id === project.id;
      html += '<a class="proj ' + (active ? 'active' : '') + '" href="#/project/' + p.id + '/home" title="' + esc(p.name) + '">' +
        '<span class="pdot st-' + p.status + '"></span><span class="pname">' + esc(p.name) + '</span>' +
      '</a>';
      if (active) {
        var v = (App.route && App.route.params && App.route.params.view) || 'home';
        html += '<div class="subnav">' +
          navLink('#/project/' + p.id + '/home', '', '项目首页', v === 'home') +
          navLink('#/project/' + p.id + '/build', '', '方案建设', v === 'build') +
          navLink('#/project/' + p.id + '/cases', '', '用例管理', v === 'cases') +
          navLink('#/project/' + p.id + '/run', '', '测试执行', v === 'run') +
          navLink('#/project/' + p.id + '/reports', '', '报告', v === 'reports') +
        '</div>';
      }
    });
    if (!mine.length) html += '<div class="side-empty">暂无项目，点击右侧「创建项目」开始</div>';
    html += '</div>';
    html += '<div class="nav bottom">' +
      navLink('#/settings', '⚙', '设置', context === 'settings') +
      (user && user.admin ? navLink('#/admin', '✦', 'admin 后台', context === 'admin') : '') +
    '</div>';
    html += '<div class="foot">v1.1 需求原型<br/>仅交互设计，无后端逻辑</div>';
    return html;
  }

  function navLink(href, ico, label, active) {
    return '<a href="' + href + '" class="' + (active ? 'active' : '') + '">' +
      (ico ? '<span class="ico">' + ico + '</span>' : '') + label + '</a>';
  }

  function userChip() {
    var u = ST.findUser(ST.state.currentUser);
    if (!u) return '';
    return '<div class="user" onclick="Views.userMenu()"><div class="avatar">' + esc(u.name.charAt(0)) + '</div><span>' + esc(u.name) + '</span></div>';
  }

  function userMenu() {
    UI.openModal(UI.modal('账号', '<div class="kv">' +
      '<div class="k">姓名</div><div>' + esc(ST.findUser(ST.state.currentUser).name) + '</div>' +
      '<div class="k">邮箱</div><div>' + esc(ST.findUser(ST.state.currentUser).email) + '</div>' +
    '</div>', '<button class="btn btn-ghost" onclick="UI.closeModal()">关闭</button>' +
      '<button class="btn btn-danger" onclick="Views.logout()">退出登录</button>'));
  }

  function logout() {
    ST.state.currentUser = null;
    ST.persist();
    UI.closeModal();
    location.hash = '#/login';
  }

  global.Views = {
    renderLogin: renderLogin, renderRegister: renderRegister, renderProjects: renderProjects,
    renderNewProject: renderNewProject, renderModel: renderModel, renderHome: renderHome,
    renderBuild: renderBuild, renderCases: renderCases, renderRun: renderRun,
    renderReports: renderReports, renderSettings: renderSettings, renderAdmin: renderAdmin,
    doLogin: doLogin, quickLogin: quickLogin, registerDone: registerDone, forgot: forgot,
    disclaimer: disclaimer, addAccountRow: addAccountRow, newProjectNext: newProjectNext,
    testModel: testModel, skipModel: skipModel, finishModel: finishModel,
    projectSettings: projectSettings, delAccount: delAccount, startBuild: startBuild, stopBuild: stopBuild,
    caseDetail: caseDetail, runCase: runCase, renderDebug: renderDebug, reRunDebug: reRunDebug,
    startRun: startRun, stopRun: stopRun,
    genReport: genReport, reportDetail: reportDetail, resetDemo: resetDemo,
    deleteProject: deleteProject, userMenu: userMenu, logout: logout
  };
})(window);
