/* 数据层：模拟数据 + localStorage 持久化 */
(function (global) {
  'use strict';

  var KEY = 'sighttest-proto-v1';

  function seed() {
    return {
      currentUser: null,
      users: [
        { id: 'u1', name: '林小满', email: 'dev@example.com', admin: false, status: 'normal' },
        { id: 'u2', name: '陈放', email: 'qa@example.com', admin: false, status: 'normal' },
        { id: 'u3', name: '王哲', email: 'ops@example.com', admin: false, status: 'frozen' },
        { id: 'admin', name: '平台管理员', email: 'admin@sighttest.io', admin: true, status: 'normal' }
      ],
      platform: {
        totalConcurrency: 5,
        globalStressLimit: 100,
        perAccountLimit: 10,
        accountCap: 10,
        defaultExploreMinutes: 60,
        defaultExplorePages: 200,
        retentionDays: 90,
        stressDuration: 60,
        disclaimer: '本平台仅供内部待测站点进行测试，用户需保证对被测站点拥有合法测试授权，并自行承担测试行为产生的一切后果。'
      },
      modelConfigs: [
        { id: 'm1', name: 'gpt-4o-mini', baseUrl: 'https://api.openai.com/v1', key: 'sk-••••1234', ok: true, latest: true },
        { id: 'm2', name: 'glm-4-flash', baseUrl: 'https://open.bigmodel.cn/api', key: '••••8899', ok: true, latest: false },
        { id: 'm3', name: 'qwen-vl-max', baseUrl: 'https://dashscope.aliyuncs.com', key: 'sk-••••4321', ok: false, latest: false }
      ],
      projects: [
        {
          id: 'p1', name: '云上商城', url: 'https://shop.example.com', creator: 'u1',
          status: 'ready', planIncomplete: false, version: 3,
          accounts: [
            { id: 'a1', user: 'buyer01', pass: 'Pass@2026', main: true, login: 'ok', lastLogin: '今天 09:12' },
            { id: 'a2', user: 'buyer02', pass: 'Pass@2026', main: false, login: 'ok', lastLogin: '今天 09:13' },
            { id: 'a3', user: 'buyer03', pass: 'Pass@2026', main: false, login: 'fail', lastLogin: '昨天 18:40', failReason: '验证码识别失败' }
          ],
          model: 'm1', activeDiscovery: true, perAccountLimit: 10,
          explored: { pages: 42, funcs: 18, apis: 26, minutes: 36, html: true, js: true, network: true }
        },
        {
          id: 'p2', name: '协作办公台', url: 'https://office.example.com', creator: 'u1',
          status: 'building', planIncomplete: false, version: 2,
          accounts: [{ id: 'a4', user: 'staff01', pass: 'Pass@2026', main: true, login: 'ok', lastLogin: '进行中' }],
          model: 'm1', activeDiscovery: true, perAccountLimit: 10,
          explored: { pages: 18, funcs: 9, apis: 11, minutes: 14, html: true, js: true, network: true }
        },
        {
          id: 'p3', name: '内容社区', url: 'https://forum.example.com', creator: 'u1',
          status: 'empty', planIncomplete: false, version: 0,
          accounts: [{ id: 'a5', user: 'member01', pass: 'Pass@2026', main: true, login: 'unused', lastLogin: '—' }],
          model: 'm2', activeDiscovery: true, perAccountLimit: 10,
          explored: { pages: 0, funcs: 0, apis: 0, minutes: 0, html: false, js: false, network: false }
        },
        {
          id: 'p4', name: '商城 App 后台', url: 'https://admin.example.com', creator: 'u2',
          status: 'ready', planIncomplete: true, version: 1,
          accounts: [{ id: 'a6', user: 'admin01', pass: 'Pass@2026', main: true, login: 'ok', lastLogin: '昨天 15:02' }],
          model: 'm1', activeDiscovery: false, perAccountLimit: 10,
          explored: { pages: 27, funcs: 14, apis: 20, minutes: 60, html: true, js: true, network: true }
        },
        {
          id: 'p5', name: '在线教育', url: 'https://edu.example.com', creator: 'u1',
          status: 'ready', planIncomplete: false, version: 5,
          accounts: [{ id: 'a7', user: 'stu01', pass: 'Pass@2026', main: true, login: 'ok', lastLogin: '上周五' }],
          model: 'm3', activeDiscovery: true, perAccountLimit: 10,
          explored: { pages: 56, funcs: 24, apis: 33, minutes: 51, html: true, js: true, network: true }
        }
      ],
      cases: [],
      executions: [],
      reports: [],
      issues: []
    };
  }

  // 生成演示用例
  function genCases() {
    var cases = [];
    var id = 1;
    function add(c) { c.id = 'c' + (id++); cases.push(c); return c; }

    // 功能用例
    var funcs = [
      ['首页', '首页', '首页正常加载', 'P0', 'pass'],
      ['商品', '商品列表', '按分类筛选商品', 'P0', 'pass'],
      ['商品', '商品详情', '详情页展示规格与库存', 'P0', 'pass'],
      ['商品', '商品详情', '无库存时置灰购买按钮', 'P1', 'fail'],
      ['购物车', '购物车', '加入购物车并校验数量', 'P0', 'pass'],
      ['购物车', '购物车', '删除购物车商品', 'P1', 'pass'],
      ['下单', '结算页', '提交订单并支付', 'P0', 'blocked'],
      ['下单', '结算页', '优惠券抵扣金额', 'P1', 'pass'],
      ['个人中心', '我的订单', '查看订单列表', 'P1', 'pass'],
      ['个人中心', '账号设置', '修改收货地址', 'P2', 'none'],
      ['个人中心', '账号设置', '注销账号（不可自动化）', 'P2', 'none'],
      ['登录注册', '登录', '手机号验证码登录', 'P0', 'blocked']
    ];
    funcs.forEach(function (f, i) {
      add({ type: 'func', module: f[0], page: f[1], name: f[2], priority: f[3], result: f[4],
        automatable: f[4] !== 'none' ? 'yes' : 'no', steps: '1. 打开页面\n2. 执行对应操作\n3. 校验预期结果',
        expect: '页面正常展示，数据与操作符合预期', marks: i === 4 ? ['已自动修复'] : (i === 9 ? ['人工新增'] : []) });
    });

    // 接口用例
    var apis = [
      ['POST', '/api/goods/list', '商品列表', 'normal', 'pass'],
      ['POST', '/api/goods/list', '商品列表', 'mutation', 'pass'],
      ['GET', '/api/goods/{id}', '商品详情', 'normal', 'pass'],
      ['GET', '/api/goods/{id}', '商品详情', 'security', 'fail'],
      ['POST', '/api/cart/add', '加入购物车', 'normal', 'pass'],
      ['POST', '/api/cart/add', '加入购物车', 'mutation', 'pass'],
      ['POST', '/api/order/create', '创建订单', 'normal', 'pass'],
      ['POST', '/api/order/create', '创建订单', 'security', 'pass'],
      ['GET', '/api/order/{id}', '订单详情', 'normal', 'pass'],
      ['GET', '/api/order/{id}', '订单详情', 'security', 'pass']
    ];
    apis.forEach(function (a) {
      var kind = a[3] === 'normal' ? '正常用例' : (a[3] === 'mutation' ? '参数变异' : '安全变异');
      add({ type: 'api', module: a[2], page: a[0] + ' ' + a[1], name: a[2] + ' · ' + kind,
        priority: a[3] === 'normal' ? 'P0' : 'P1', result: a[4], automatable: 'yes',
        steps: '请求 ' + a[0] + ' ' + a[1], expect: 'HTTP 2xx，业务 code=0',
        apiMethod: a[0], apiPath: a[1], apiKind: a[3] });
    });

    // 性能用例
    var pages = ['/', '/goods/list', '/goods/detail', '/cart', '/checkout', '/user/orders'];
    pages.forEach(function (p, i) {
      add({ type: 'perf', module: '页面加载', page: p, name: '页面加载 · ' + p + ' · 首次加载',
        priority: 'P2', result: i === 2 ? 'fail' : 'pass', automatable: 'yes',
        scenario: '首次加载', metric: 'LCP 2.1s / 完整加载 4.3s', expect: 'LCP ≤ 2.5s，完整加载 ≤ 5s' });
    });
    ['/api/goods/list', '/api/goods/{id}', '/api/order/create', '/api/cart/add'].forEach(function (p, i) {
      add({ type: 'perf', module: '接口压测', page: p, name: '接口压测 · ' + p,
        priority: 'P1', result: i === 0 ? 'pass' : 'none', automatable: 'yes',
        scenario: '并发 30 · 持续 60s', metric: i === 0 ? '平均 320ms · P95 780ms · 错误率 0.2%' : '—',
        expect: '平均 ≤ 500ms，P95 ≤ 1s，错误率 ≤ 1%', concurrency: 30, duration: 60 });
    });

    // 机制用例
    [
      ['SEO', '搜索引擎优化', '标题与描述、结构化数据、sitemap', 'pass'],
      ['推广', '社交分享卡片', '分享标题、图片、摘要', 'fail'],
      ['推广', '推广落地页', '带 utm 参数访问与统计上报', 'pass'],
      ['直出', '服务端渲染直出', '首屏 HTML 包含主内容', 'none']
    ].forEach(function (m) {
      add({ type: 'mech', module: m[0], page: '全站', name: m[1], priority: 'P2', result: m[3],
        automatable: 'yes', steps: m[2], expect: '检查规则全部通过' });
    });

    return cases;
  }

  function seedIssues() {
    return [
      { id: 'i1', severity: '严重', page: '/goods/detail', desc: '规格切换后价格区域空白，疑似前端渲染异常', status: '确认', cases: ['c4'], time: '今天 10:22' },
      { id: 'i2', severity: '一般', page: '/cart', desc: '删除按钮 hover 态与设计稿不一致', status: '误报', cases: [], time: '今天 10:20' },
      { id: 'i3', severity: '一般', page: '/checkout', desc: '优惠券金额未保留两位小数', status: '确认', cases: ['c8'], time: '昨天 16:40' },
      { id: 'i4', severity: '提示', page: '/user/orders', desc: '订单列表缺少空状态占位图', status: '确认', cases: [], time: '昨天 16:38' }
    ];
  }

  function seedExecutions() {
    return [
      {
        id: 'e1', project: 'p1', name: '全量测试 · 第 6 次', status: 'done',
        progress: 100, startedAt: '今天 09:20', finishedAt: '今天 10:31', version: 3,
        order: ['功能', '接口', '页面加载性能', '网站机制', '接口压测'],
        summary: { pass: 38, fail: 3, blocked: 2, none: 4 }
      },
      {
        id: 'e2', project: 'p1', name: '接口压测（3 账号交叉）', status: 'running',
        progress: 64, startedAt: '今天 11:02', finishedAt: null, version: 3,
        order: ['接口压测'], summary: { pass: 12, fail: 0, blocked: 0, none: 0 },
        accounts: [
          { user: 'buyer01', req: 4120, err: 0.1 },
          { user: 'buyer02', req: 4080, err: 0.3 },
          { user: 'buyer03', req: 0, err: null, skip: '登录失败' }
        ]
      },
      {
        id: 'e3', project: 'p5', name: '单项测试 · 接口', status: 'done',
        progress: 100, startedAt: '上周五', finishedAt: '上周五', version: 5,
        order: ['接口'], summary: { pass: 21, fail: 1, blocked: 0, none: 0 }
      }
    ];
  }

  function seedReports() {
    return [
      {
        id: 'r1', project: 'p1', title: '云上商城 · 全量测试报告', scope: '全量测试 · 第 6 次',
        score: 82, risk: '中', time: '今天 10:35', version: 3,
        top: ['商品详情规格切换渲染异常（严重）', '无库存时购买按钮未置灰（不通过）', '优惠券金额精度错误（一般）'],
        summary: '本次全量测试共执行 47 条用例，通过 38 条。核心购买链路可用，但商品详情页存在一处严重渲染缺陷，建议优先修复后回归。'
      },
      {
        id: 'r2', project: 'p5', title: '在线教育 · 接口测试报告', scope: '单项测试 · 接口',
        score: 91, risk: '低', time: '上周五', version: 5,
        top: ['课程详情接口偶发超时'],
        summary: '接口整体稳定，仅课程详情接口在高峰期偶发超时，建议关注。'
      }
    ];
  }

  function load() {
    var raw = null;
    try { raw = localStorage.getItem(KEY); } catch (e) {}
    if (raw) {
      try { return JSON.parse(raw); } catch (e) {}
    }
    var s = seed();
    s.cases = genCases();
    s.executions = seedExecutions();
    s.reports = seedReports();
    s.issues = seedIssues();
    return s;
  }

  var state = load();

  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }

  function reset() {
    try { localStorage.removeItem(KEY); } catch (e) {}
    state = load();
  }

  function save() { persist(); }

  // 工具
  function findProject(id) {
    return state.projects.find(function (p) { return p.id === id; });
  }
  function findUser(id) {
    return state.users.find(function (u) { return u.id === id; });
  }
  function projectCases(projectId) {
    return state.cases.filter(function (c) {
      // 演示：所有用例挂在 p1/p5 下
      return projectId === 'p1' || projectId === 'p5';
    });
  }

  function uid(prefix) {
    return prefix + '-' + Math.random().toString(36).slice(2, 8);
  }

  global.ST = {
    KEY: KEY, state: state, persist: persist, reset: reset, save: save,
    findProject: findProject, findUser: findUser, projectCases: projectCases, uid: uid
  };
})(window);
