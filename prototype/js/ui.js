/* 共享 UI 工具与组件 */
(function (global) {
  'use strict';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
  }

  function toast(msg, type) {
    var root = document.getElementById('toast-root');
    var el = document.createElement('div');
    var t = type || '';
    var icon = t === 'ok' ? '✓' : t === 'fail' ? '!' : 'i';
    el.className = 'toast' + (t ? ' ' + t : '');
    el.innerHTML = '<span class="t-ico">' + icon + '</span><span>' + esc(msg) + '</span>';
    root.appendChild(el);
    setTimeout(function () {
      el.style.opacity = '0';
      el.style.transition = 'opacity .3s';
      setTimeout(function () { el.remove(); }, 300);
    }, 2400);
  }

  function openModal(html, width) {
    var root = document.getElementById('modal-root');
    root.innerHTML =
      '<div class="modal-mask" id="modal-mask">' +
        '<div class="modal" style="' + (width ? 'width:' + width + 'px' : '') + '">' + html + '</div>' +
      '</div>';
    var mask = document.getElementById('modal-mask');
    mask.addEventListener('click', function (e) {
      if (e.target === mask) closeModal();
    });
  }

  function closeModal() {
    document.getElementById('modal-root').innerHTML = '';
  }

  function badge(result) {
    var map = {
      'pass': ['badge-ok', '通过'],
      'fail': ['badge-fail', '不通过'],
      'blocked': ['badge-blocked', '阻塞'],
      'none': ['badge-none', '未执行']
    };
    var m = map[result] || map.none;
    return '<span class="badge ' + m[0] + '">' + m[1] + '</span>';
  }

  function pBadge(p) {
    return '<span class="badge ' + p.toLowerCase() + '">' + p + '</span>';
  }

  function statusBadge(status) {
    var map = {
      'ready': ['badge-ok', '已就绪'],
      'building': ['badge-brand', '建设中'],
      'empty': ['badge-none', '空项目'],
      'failed': ['badge-fail', '建设失败']
    };
    var m = map[status] || map.empty;
    return '<span class="badge ' + m[0] + '">' + m[1] + '</span>';
  }

  function progressBar(pct, cls) {
    return '<div class="progress ' + (cls || '') + '"><i style="width:' + pct + '%"></i></div>';
  }

  function riskHtml(risk) {
    return '<span class="' + (risk === '高' ? 'risk-high' : risk === '中' ? 'risk-mid' : 'risk-low') + '">' + risk + '</span>';
  }

  function ring(score) {
    var c = 2 * Math.PI * 40;
    var color = score >= 85 ? 'var(--ok)' : score >= 60 ? 'var(--blocked)' : 'var(--fail)';
    return '<div class="ring">' +
      '<svg width="96" height="96">' +
        '<circle cx="48" cy="48" r="40" fill="none" stroke="#e9edf5" stroke-width="8"/>' +
        '<circle cx="48" cy="48" r="40" fill="none" stroke="' + color + '" stroke-width="8" stroke-linecap="round"' +
          ' stroke-dasharray="' + c + '" stroke-dashoffset="' + (c * (1 - score / 100)) + '"/>' +
      '</svg><div class="val">' + score + '</div></div>';
  }

  function modal(title, body, foot) {
    return '<div class="modal-h"><div class="t">' + esc(title) + '</div>' +
      '<button class="btn btn-ghost btn-sm" onclick="UI.closeModal()">✕</button></div>' +
      '<div class="modal-b">' + body + '</div>' +
      (foot ? '<div class="modal-f">' + foot + '</div>' : '');
  }

  global.UI = {
    esc: esc, toast: toast, openModal: openModal, closeModal: closeModal,
    badge: badge, pBadge: pBadge, statusBadge: statusBadge, progressBar: progressBar,
    riskHtml: riskHtml, ring: ring, modal: modal
  };
})(window);
