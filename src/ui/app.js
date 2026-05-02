/**
 * 飞站 - UI交互脚本
 * 4步向导: 类型 -> 风格 -> 功能 -> 生成
 */
(function() {
  'use strict';

  // ============================
  // 状态管理
  // ============================
  var state = {
    step: 1,
    selectedType: null,     // {key, name, desc}
    selectedStyle: null,    // {key, name, desc, color}
    selectedFeatures: [],   // string[]
    pages: 1,               // 层级
    content: { title: '', subtitle: '', about: '' },
    history: [],            // 历史记录
    generating: false,
    configLoaded: false
  };

  // 配置数据
  var config = { types: {}, styles: {}, features: {} };

  // ============================
  // DOM 引用
  // ============================
  var $ = function(id) { return document.getElementById(id); };

  // ============================
  // 初始化
  // ============================
  function init() {
    loadHistory();
    fetchConfig();
    bindEvents();
  }

  function fetchConfig() {
    fetch('/api/config')
      .then(function(r) { return r.json(); })
      .then(function(data) {
        config.types = data.website_types || {};
        config.styles = data.design_styles || {};
        config.features = data.features || {};
        state.configLoaded = true;
        renderTypeGrid();
        renderStyleGrid();
        renderFeatureGrid();
      })
      .catch(function(e) {
        console.error('加载配置失败:', e);
      });
  }

  function bindEvents() {
    $('prevBtn').addEventListener('click', prevStep);
    $('nextBtn').addEventListener('click', nextStep);
    $('generateBtn').addEventListener('click', generate);
    $('codeBtn').addEventListener('click', toggleCodeView);
    $('exportBtn').addEventListener('click', exportCode);
    $('clearHistoryBtn').addEventListener('click', clearHistory);

    // 自定义内容输入
    $('siteTitle').addEventListener('input', function() { state.content.title = this.value; });
    $('siteSubtitle').addEventListener('input', function() { state.content.subtitle = this.value; });
    $('siteAbout').addEventListener('input', function() { state.content.about = this.value; });
  }

  // ============================
  // 渲染函数
  // ============================
  function renderTypeGrid() {
    var grid = $('typeGrid');
    var html = '';
    var typeEmojis = { company: '🏢', product: '📦', portfolio: '🎨', blog: '📝', forum: '💬' };
    Object.keys(config.types).forEach(function(key) {
      var t = config.types[key];
      html += '<div class="type-card" data-type="' + key + '">' +
        '<h3>' + (typeEmojis[key] || '') + ' ' + t.name + '</h3>' +
        '<p>' + t.description + '</p>' +
      '</div>';
    });
    grid.innerHTML = html;
    grid.addEventListener('click', function(e) {
      var card = e.target.closest('.type-card');
      if (!card) return;
      var els = grid.querySelectorAll('.type-card');
      for (var i = 0; i < els.length; i++) els[i].classList.remove('selected');
      card.classList.add('selected');
      state.selectedType = { key: card.dataset.type, name: config.types[card.dataset.type].name, desc: config.types[card.dataset.type].description };
      updateGenerateBtn();
    });
  }

  function renderStyleGrid() {
    var grid = $('styleGrid');
    var html = '';
    var styleColors = {
      modern: '#2563eb', minimal: '#000000', bento: '#8b5cf6', brutalist: '#dc2626', glass: '#0ea5e9',
      neumorphic: '#6366f1', gradient: '#f97316', dark: '#22d3d1', cyber: '#ff0080', nature: '#16a34a'
    };
    Object.keys(config.styles).forEach(function(key) {
      var s = config.styles[key];
      var color = styleColors[key] || '#888';
      html += '<div class="style-card" data-style="' + key + '">' +
        '<div class="style-preview" style="background:' + color + ';">' + s.name.substring(0,2) + '</div>' +
        '<h3>' + s.name + '</h3>' +
        '<p>' + s.description + '</p>' +
      '</div>';
    });
    grid.innerHTML = html;
    grid.addEventListener('click', function(e) {
      var card = e.target.closest('.style-card');
      if (!card) return;
      var els = grid.querySelectorAll('.style-card');
      for (var i = 0; i < els.length; i++) els[i].classList.remove('selected');
      card.classList.add('selected');
      state.selectedStyle = { key: card.dataset.style, name: config.styles[card.dataset.style].name, desc: config.styles[card.dataset.style].description, color: styleColors[card.dataset.style] };
      updateGenerateBtn();
    });
  }

  function renderFeatureGrid() {
    var grid = $('featureGrid');
    var html = '';
    Object.keys(config.features).forEach(function(key) {
      html += '<label class="feature-card" data-feature="' + key + '">' +
        '<input type="checkbox" value="' + key + '" style="display:none;">' +
        '<span class="cb">&#x2713;</span>' +
        '<span>' + config.features[key] + '</span>' +
      '</label>';
    });
    grid.innerHTML = html;
    grid.addEventListener('change', function(e) {
      if (e.target.type !== 'checkbox') return;
      var card = e.target.closest('.feature-card');
      if (e.target.checked) {
        card.classList.add('selected');
        if (state.selectedFeatures.indexOf(e.target.value) === -1) {
          state.selectedFeatures.push(e.target.value);
        }
      } else {
        card.classList.remove('selected');
        state.selectedFeatures = state.selectedFeatures.filter(function(f) { return f !== e.target.value; });
      }
    });

    // 层级选择
    var levelInputs = document.querySelectorAll('input[name="pages"]');
    for (var i = 0; i < levelInputs.length; i++) {
      levelInputs[i].addEventListener('change', function() {
        state.pages = parseInt(this.value);
      });
    }
  }

  // ============================
  // 步骤导航
  // ============================
  function prevStep() {
    if (state.generating) return;
    if (state.step > 1) {
      state.step--;
      updateSteps();
    }
  }

  function nextStep() {
    if (state.generating) return;

    // 验证
    if (state.step === 1 && !state.selectedType) {
      shakeElement($('typeGrid'));
      return;
    }
    if (state.step === 2 && !state.selectedStyle) {
      shakeElement($('styleGrid'));
      return;
    }

    if (state.step < 4) {
      state.step++;
      updateSteps();
    }

    if (state.step === 4) {
      updateSummary();
    }
  }

  /** 抖动提示 */
  function shakeElement(el) {
    el.style.animation = 'none';
    el.offsetHeight; // reflow
    el.style.animation = 'shake 0.5s ease';
    setTimeout(function() { el.style.animation = ''; }, 500);
  }

  function updateSteps() {
    // 更新步骤指示器
    var steps = document.querySelectorAll('.step');
    for (var i = 0; i < steps.length; i++) {
      var s = parseInt(steps[i].dataset.step);
      steps[i].classList.toggle('active', s === state.step);
    }
    // 更新内容区
    for (var j = 1; j <= 4; j++) {
      var section = document.getElementById('step' + j);
      if (section) section.classList.toggle('active', j === state.step);
    }
    // 按钮
    $('prevBtn').disabled = state.step === 1;
    $('nextBtn').textContent = state.step === 4 ? '完成' : '下一步';
    $('stepIndicator').textContent = state.step + ' / 4';

    // 隐藏结果
    $('resultSection').style.display = 'none';
  }

  function updateGenerateBtn() {
    if (state.selectedType && state.selectedStyle) {
      $('generateBtn').disabled = false;
    }
  }

  function updateSummary() {
    $('smType').textContent = state.selectedType ? state.selectedType.name : '-';
    $('smStyle').textContent = state.selectedStyle ? state.selectedStyle.name : '-';
    $('smFeatures').textContent = state.selectedFeatures.length > 0
      ? state.selectedFeatures.map(function(f) { return config.features[f] || f; }).join('、')
      : '默认模块';
    $('smPages').textContent = state.pages + '层';
  }

  // ============================
  // 生成网站
  // ============================
  function generate() {
    if (state.generating) return;
    state.generating = true;

    var btn = $('generateBtn');
    var progressContainer = $('progressContainer');
    var progressFill = $('progressFill');
    var progressText = $('progressText');
    var statusBox = $('statusBox');

    btn.disabled = true;
    btn.style.display = 'none';
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = '正在初始化...';
    statusBox.textContent = '';
    statusBox.className = 'status-box';
    $('resultSection').style.display = 'none';

    // 模拟进度动画
    var progressInterval = setInterval(function() {
      var w = parseFloat(progressFill.style.width) || 0;
      if (w < 90) {
        progressFill.style.width = (w + Math.random() * 15) + '%';
      }
    }, 400);

    // 发送生成请求
    fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: state.selectedType.key,
        style: state.selectedStyle.key,
        pages: state.pages,
        features: state.selectedFeatures,
        content: state.content
      })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      clearInterval(progressInterval);
      progressFill.style.width = '100%';

      if (data.success) {
        progressText.textContent = '生成完成!';
        statusBox.textContent = '网站已生成，可预览或导出';
        statusBox.className = 'status-box success';
        setTimeout(function() { showResult(data.output); }, 500);
      } else {
        statusBox.textContent = '生成失败: ' + data.error;
        statusBox.className = 'status-box error';
        showError(data);
      }
    })
    .catch(function(e) {
      clearInterval(progressInterval);
      statusBox.textContent = '网络请求失败: ' + e.message;
      statusBox.className = 'status-box error';
      showError({ error: e.message, detail: '请确保服务器正常运行 (python feizhan.py --ui)' });
    })
    .finally(function() {
      state.generating = false;
      btn.disabled = false;
      btn.style.display = 'block';
      $('progressContainer').style.display = 'none';
    });
  }

  function showResult(outputPath) {
    var rs = $('resultSection');
    $('resultSuccess').style.display = 'block';
    $('resultError').style.display = 'none';

    // 预览链接
    $('previewBtn').href = '/outputs/' + outputPath.split(/[\\/]/).pop() + '/index.html';
    $('previewBtn').dataset.outputPath = outputPath;

    // 网站预览卡片
    $('sitePreview').innerHTML =
      '<p style="margin-bottom:8px;"><strong>' + (state.selectedType ? state.selectedType.name : '') + '</strong></p>' +
      '<p style="font-size:.7rem;">风格: ' + (state.selectedStyle ? state.selectedStyle.name : '') + ' | ' +
      state.pages + '层 | ' + new Date().toLocaleString() + '</p>' +
      '<p style="font-size:.7rem;color:var(--c-text2);">' + outputPath.split(/[\\/]/).pop() + '</p>';

    rs.style.display = 'block';

    // 获取代码结构
    fetchCodeTree(outputPath);

    // 保存到历史
    addToHistory(outputPath);

    // 滚动到结果
    rs.scrollIntoView({ behavior: 'smooth' });
  }

  function fetchCodeTree(outputPath) {
    fetch('/api/tree?path=' + encodeURIComponent(outputPath))
      .then(function(r) { return r.json(); })
      .then(function(data) {
        $('codeTree').textContent = data.tree || '（无法获取目录结构）';
      })
      .catch(function() {
        $('codeTree').textContent = '（无法获取目录结构）';
      });
  }

  function showError(data) {
    var rs = $('resultSection');
    $('resultSuccess').style.display = 'none';
    $('resultError').style.display = 'block';
    $('errorMsg').textContent = data.error || '未知错误';
    $('errorDetail').textContent = data.detail || data.error || '';
    rs.style.display = 'block';
  }

  function toggleCodeView() {
    var cs = $('codeStructure');
    cs.style.display = cs.style.display === 'none' ? 'block' : 'none';
  }

  // ============================
  // 导出代码
  // ============================
  function exportCode() {
    var outputPath = ($('previewBtn').dataset.outputPath || '').replace(/\\/g, '/');
    if (!outputPath) {
      alert('请先生成网站');
      return;
    }

    // 提示 - 实际导出需要服务端支持ZIP打包
    alert('导出功能需要服务端支持ZIP打包。当前版本请直接复制文件夹:\n' + outputPath);

    // 尝试打开文件夹
    if (window.confirm('是否在资源管理器中打开该文件夹？')) {
      fetch('/api/open?path=' + encodeURIComponent(outputPath)).catch(function() {});
    }
  }

  // ============================
  // 历史记录
  // ============================
  function loadHistory() {
    try {
      var saved = localStorage.getItem('feizhan_history_v2');
      if (saved) {
        state.history = JSON.parse(saved);
        renderHistory();
      }
    } catch(e) {
      state.history = [];
    }
  }

  function addToHistory(outputPath) {
    var item = {
      typeKey: state.selectedType ? state.selectedType.key : 'company',
      typeName: state.selectedType ? state.selectedType.name : '未知',
      styleKey: state.selectedStyle ? state.selectedStyle.key : 'modern',
      styleName: state.selectedStyle ? state.selectedStyle.name : '未知',
      features: state.selectedFeatures.slice(),
      pages: state.pages,
      outputPath: outputPath,
      folderName: outputPath.split(/[\\/]/).pop(),
      time: new Date().toLocaleString()
    };
    state.history.unshift(item);
    if (state.history.length > 20) state.history.length = 20;

    try {
      localStorage.setItem('feizhan_history_v2', JSON.stringify(state.history));
    } catch(e) {}

    renderHistory();
  }

  function renderHistory() {
    var list = $('historyList');
    var clearBtn = $('clearHistoryBtn');

    if (state.history.length === 0) {
      list.innerHTML = '<p class="empty-state">暂无历史记录，来生成第一个网站吧!</p>';
      clearBtn.style.display = 'none';
      return;
    }

    clearBtn.style.display = 'inline-block';

    var html = '';
    state.history.forEach(function(item, idx) {
      html += '<div class="history-item">' +
        '<div class="hi-info">' +
          '<div class="hi-name"><strong>' + item.typeName + '</strong> · ' + item.styleName + ' · ' + item.pages + '层</div>' +
          '<div class="hi-meta">' + item.folderName + ' | ' + item.time + '</div>' +
        '</div>' +
        '<div class="hi-actions">' +
          '<a href="/outputs/' + item.folderName + '/index.html" target="_blank" class="hi-btn">预览</a>' +
          '<button class="hi-btn" onclick="window._regenerateHistory(' + idx + ')">重新生成</button>' +
          '<button class="hi-btn danger" onclick="window._deleteHistory(' + idx + ')">删除</button>' +
        '</div>' +
      '</div>';
    });
    list.innerHTML = html;
  }

  // 暴露给全局
  window._regenerateHistory = function(idx) {
    var item = state.history[idx];
    if (!item) return;
    state.selectedType = { key: item.typeKey, name: item.typeName };
    state.selectedStyle = { key: item.styleKey, name: item.styleName };
    state.selectedFeatures = item.features.slice();
    state.pages = item.pages;
    state.step = 4;
    updateSteps();
    updateSummary();
    $('generateBtn').disabled = false;
    $('resultSection').style.display = 'none';
  };

  window._deleteHistory = function(idx) {
    if (!confirm('确定要删除这条历史记录吗？')) return;
    state.history.splice(idx, 1);
    try {
      localStorage.setItem('feizhan_history_v2', JSON.stringify(state.history));
    } catch(e) {}
    renderHistory();
  };

  function clearHistory() {
    if (!confirm('确定要清空所有历史记录吗？此操作不可撤销。')) return;
    state.history = [];
    localStorage.removeItem('feizhan_history_v2');
    renderHistory();
  }

  // ============================
  // 键盘导航
  // ============================
  document.addEventListener('keydown', function(e) {
    if (state.generating) return;
    if (e.key === 'ArrowRight' && !e.target.closest('input,textarea')) {
      nextStep();
    } else if (e.key === 'ArrowLeft' && !e.target.closest('input,textarea')) {
      prevStep();
    }
  });

  // ============================
  // 全局抖动动画
  // ============================
  var shakeStyle = document.createElement('style');
  shakeStyle.textContent =
    '@keyframes shake {' +
    '  0%,100% { transform: translateX(0); }' +
    '  25% { transform: translateX(-6px); }' +
    '  50% { transform: translateX(6px); }' +
    '  75% { transform: translateX(-4px); }' +
    '}';
  document.head.appendChild(shakeStyle);

  // ============================
  // 启动
  // ============================
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
