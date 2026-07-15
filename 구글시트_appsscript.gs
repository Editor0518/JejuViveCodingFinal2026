/**
 * 한자 작명 도우미 — 구글 스프레드시트 백엔드 (Apps Script 웹앱)
 * ---------------------------------------------------------------
 * 스프레드시트('한자 작명 사이트')의 두 탭을 읽어 JSON으로 반환합니다.
 *   · 한자 목록 탭   : 한글 글자별 인명용 한자 (한글/한자/뜻/성씨/시행일 …)
 *   · 개정연혁 탭     : 인명용 한자 제도 개정 연혁
 *
 * 열(헤더) 이름만 맞으면 순서가 달라도 됩니다. 아래 HEADERS 의 별칭 중
 * 하나로만 헤더를 만들어 두면 자동으로 인식합니다. (탭 이름도 자동 감지)
 *
 * ── 배포 방법 ─────────────────────────────────────────────
 * 1) 스프레드시트에서 [확장 프로그램] → [Apps Script] 열기
 * 2) 이 파일 내용을 붙여넣기. (스크립트가 스프레드시트에 바인딩되어 있으면
 *    SPREADSHEET_ID 는 비워도 됩니다. 별도 프로젝트면 ID 를 채우세요.)
 * 3) [배포] → [새 배포] → 유형 '웹 앱'
 *      - 실행 계정: 나
 *      - 액세스 권한: '모든 사용자'  (브라우저에서 fetch 하려면 필수)
 * 4) 생성된 '웹 앱 URL' 을 복사해 작명도우미.html 의
 *    SHEET_API_URL 에 붙여넣으세요.
 * 5) 시트 값을 바꾼 뒤에는 재배포 없이 바로 반영됩니다.
 *    (코드를 바꿨을 때만 [배포 관리]에서 새 버전으로 업데이트)
 */

var CONFIG = {
  // 스크립트가 스프레드시트에 바인딩돼 있으면 '' 로 두세요.
  // 독립 프로젝트면 스프레드시트 URL 의 /d/ 와 /edit 사이 ID 를 넣으세요.
  SPREADSHEET_ID: '',
  // 탭 이름을 지정하면 자동 감지보다 우선합니다. 비워두면 헤더로 자동 감지.
  HANJA_SHEET: '',
  HISTORY_SHEET: '',
  TIMEZONE: 'Asia/Seoul'
};

// 헤더 별칭 (왼쪽부터 우선 매칭)
var HEADERS = {
  syllable: ['한글', '독음', '소리', '한글독음'],
  hanja:    ['한자', '한자표기'],
  meaning:  ['뜻', '훈', '한글뜻', '뜻(한글)', '훈음', '의미'],
  meaningEn:['뜻_영문참고', '영문뜻', '뜻영문', '영문의미'],
  surname:  ['성씨', '성씨여부', '성', '姓', '성씨한자'],
  date:     ['시행일', '추가일', '인명용추가일', '추가시행일', '추가된날짜'],
  ohaeng:   ['발음오행', '오행'],
  stroke:   ['총획수', '획수'],
  radical:  ['부수'],
  unicode:  ['유니코드'],
  // 개정연혁
  year:     ['연도', '년도', 'year'],
  effDate:  ['시행일'],
  added:    ['추가된_글자수', '추가글자수', '추가 글자수', '추가된글자수'],
  total:    ['누적_총_글자수', '누적총글자수', '누적 총 글자수', '총글자수'],
  law:      ['근거법령', '법령', '근거'],
  note:     ['비고', '메모', '설명']
};

function doGet(e) {
  try {
    var ss = CONFIG.SPREADSHEET_ID
      ? SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID)
      : SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) throw new Error('스프레드시트를 찾을 수 없습니다. SPREADSHEET_ID 를 확인하세요.');

    var picked = pickSheets(ss);
    if (!picked.hanja) throw new Error('한자 목록 탭을 찾지 못했습니다. (헤더에 "한글","한자" 필요)');

    var hanja = buildHanja(picked.hanja);
    var history = picked.history ? buildHistory(picked.history) : [];

    var count = 0;
    Object.keys(hanja).forEach(function (k) { count += hanja[k].length; });

    return json({
      hanja: hanja,
      history: history,
      meta: {
        hanjaCount: count,
        syllableCount: Object.keys(hanja).length,
        historyRows: history.length,
        hanjaSheet: picked.hanja.getName(),
        historySheet: picked.history ? picked.history.getName() : null,
        generatedAt: new Date().toISOString()
      }
    });
  } catch (err) {
    return json({ error: String((err && err.message) || err) });
  }
}

/** 탭 자동 감지: 헤더로 한자 목록/개정연혁 탭을 구분 */
function pickSheets(ss) {
  var sheets = ss.getSheets();
  var hanja = CONFIG.HANJA_SHEET ? ss.getSheetByName(CONFIG.HANJA_SHEET) : null;
  var history = CONFIG.HISTORY_SHEET ? ss.getSheetByName(CONFIG.HISTORY_SHEET) : null;

  sheets.forEach(function (sh) {
    var lastCol = sh.getLastColumn();
    if (lastCol < 1) return;
    var head = sh.getRange(1, 1, 1, lastCol).getValues()[0].map(function (x) {
      return String(x).trim();
    });
    var has = function (aliases) {
      return aliases.some(function (a) { return head.indexOf(a) >= 0; });
    };
    // 개정연혁: 연도/누적 총 글자수가 있으면 (한자 목록엔 없음)
    if (!history && has(HEADERS.year) && (has(HEADERS.total) || has(HEADERS.added))) {
      history = sh;
    }
    // 한자 목록: 한자 + 한글
    if (!hanja && has(HEADERS.hanja) && has(HEADERS.syllable) && sh !== history) {
      hanja = sh;
    }
  });
  return { hanja: hanja, history: history };
}

/** 한자 목록 탭 → { '가':[{h,m,s,d,o,st}], ... } */
function buildHanja(sheet) {
  var values = sheet.getDataRange().getValues();
  if (values.length < 2) return {};
  var head = values[0].map(function (x) { return String(x).trim(); });
  var col = colFinder(head);

  var cSyl = col(HEADERS.syllable);
  var cHan = col(HEADERS.hanja);
  var cMean = col(HEADERS.meaning);
  var cMeanEn = col(HEADERS.meaningEn);
  var cSur = col(HEADERS.surname);
  var cDate = col(HEADERS.date);
  var cOh = col(HEADERS.ohaeng);
  var cStroke = col(HEADERS.stroke);

  var db = {};
  for (var r = 1; r < values.length; r++) {
    var row = values[r];
    var syl = cSyl >= 0 ? String(row[cSyl]).trim() : '';
    var h = cHan >= 0 ? String(row[cHan]).trim() : '';
    if (!syl || !h) continue;

    var m = cMean >= 0 ? String(row[cMean]).trim() : '';
    if (!m && cMeanEn >= 0) m = String(row[cMeanEn]).trim();

    var obj = { h: h, m: m };
    if (cSur >= 0 && isTrue(row[cSur])) obj.s = true;
    if (cDate >= 0) { var d = fmtDate(row[cDate]); if (d) obj.d = d; }
    if (cOh >= 0) { var o = String(row[cOh]).trim(); if (o) obj.o = o; }
    if (cStroke >= 0 && row[cStroke] !== '' && row[cStroke] != null) obj.st = row[cStroke];

    if (!db[syl]) db[syl] = [];
    db[syl].push(obj);
  }
  return db;
}

/** 개정연혁 탭 → [{year,effDate,added,total,law,note}, ...] */
function buildHistory(sheet) {
  var values = sheet.getDataRange().getValues();
  if (values.length < 2) return [];
  var head = values[0].map(function (x) { return String(x).trim(); });
  var col = colFinder(head);

  var cYear = col(HEADERS.year);
  var cEff = col(HEADERS.effDate);
  var cAdd = col(HEADERS.added);
  var cTot = col(HEADERS.total);
  var cLaw = col(HEADERS.law);
  var cNote = col(HEADERS.note);

  var rows = [];
  for (var r = 1; r < values.length; r++) {
    var row = values[r];
    var year = cYear >= 0 ? String(row[cYear]).trim() : '';
    var eff = cEff >= 0 ? fmtDate(row[cEff]) : '';
    if (!year && !eff) continue;
    rows.push({
      year: year,
      effDate: eff,
      added: cAdd >= 0 ? String(row[cAdd]).trim() : '',
      total: cTot >= 0 ? String(row[cTot]).trim() : '',
      law: cLaw >= 0 ? String(row[cLaw]).trim() : '',
      note: cNote >= 0 ? String(row[cNote]).trim() : ''
    });
  }
  return rows;
}

/* ───────── 유틸 ───────── */

function colFinder(head) {
  return function (aliases) {
    for (var i = 0; i < aliases.length; i++) {
      var idx = head.indexOf(aliases[i]);
      if (idx >= 0) return idx;
    }
    return -1;
  };
}

function isTrue(v) {
  if (v === true) return true;
  var s = String(v).trim().toUpperCase();
  return s === 'TRUE' || s === 'Y' || s === 'O' || s === '1' ||
         s === '성씨' || s === '姓' || s === '예' || s === 'YES' || s === '성';
}

function fmtDate(v) {
  if (v === '' || v == null) return '';
  if (Object.prototype.toString.call(v) === '[object Date]') {
    return Utilities.formatDate(v, CONFIG.TIMEZONE, 'yyyy-MM-dd');
  }
  var s = String(v).trim();
  if (!s) return '';
  s = s.replace(/[.\/]/g, '-').replace(/\s/g, '').replace(/-+$/, '');
  var m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
  if (m) return m[1] + '-' + ('0' + m[2]).slice(-2) + '-' + ('0' + m[3]).slice(-2);
  return s;
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
