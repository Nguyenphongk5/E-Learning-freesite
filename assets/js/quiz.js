const questionBank = [
  { id: 'html-foundations', title: 'Nền tảng HTML & CSS', subject: 'HTML & CSS', difficulty: 'Cơ bản', duration: 12, description: 'Cấu trúc trang, semantic HTML và các nguyên tắc CSS.', questions: [
    { text: 'Thẻ HTML nào biểu thị nội dung độc lập, có thể tái sử dụng như một bài viết?', options: ['<section>', '<article>', '<aside>', '<span>'], answer: 1, explanation: '<article> dùng cho nội dung độc lập, chẳng hạn bài viết hoặc tin tức.' },
    { text: 'Thuộc tính CSS nào điều khiển khoảng trống bên trong đường viền của phần tử?', options: ['margin', 'gap', 'padding', 'spacing'], answer: 2, explanation: 'padding là khoảng đệm giữa nội dung và đường viền; margin nằm bên ngoài đường viền.' },
    { text: 'Selector nào chọn phần tử có id là "menu"?', options: ['.menu', '#menu', 'menu#', '*menu'], answer: 1, explanation: 'Selector id trong CSS bắt đầu bằng ký tự #.' },
    { text: 'Thuộc tính nào giúp ảnh giữ tỷ lệ khi vừa khung chứa?', options: ['object-fit: cover', 'display: inline', 'position: fixed', 'float: left'], answer: 0, explanation: 'object-fit: cover giữ tỷ lệ ảnh và phủ kín khung, có thể cắt phần ảnh dư.' },
    { text: 'Vai trò chính của thuộc tính alt trên ảnh là gì?', options: ['Tạo viền cho ảnh', 'Đặt kích thước ảnh', 'Cung cấp mô tả thay thế', 'Tải ảnh nhanh hơn'], answer: 2, explanation: 'alt cung cấp văn bản thay thế khi ảnh không tải được và hỗ trợ công nghệ đọc màn hình.' },
  ] },
  { id: 'javascript-basics', title: 'JavaScript căn bản', subject: 'JavaScript', difficulty: 'Cơ bản', duration: 15, description: 'Biến, kiểu dữ liệu, hàm và các thao tác với mảng.', questions: [
    { text: 'Từ khóa nào khai báo biến có thể gán lại giá trị và có phạm vi khối?', options: ['var', 'let', 'const', 'static'], answer: 1, explanation: 'let khai báo biến có phạm vi khối và cho phép gán lại giá trị.' },
    { text: 'Kết quả của biểu thức typeof null trong JavaScript là gì?', options: ['"null"', '"undefined"', '"object"', '"boolean"'], answer: 2, explanation: 'Do đặc điểm lịch sử của JavaScript, typeof null trả về "object".' },
    { text: 'Phương thức nào tạo một mảng mới bằng cách biến đổi từng phần tử?', options: ['filter()', 'map()', 'find()', 'reduceRight()'], answer: 1, explanation: 'map() biến đổi từng phần tử và trả về mảng mới.' },
    { text: 'Toán tử === kiểm tra điều gì?', options: ['Chỉ kiểm tra giá trị', 'Chỉ kiểm tra kiểu', 'Giá trị và kiểu không ép kiểu', 'Giá trị sau khi ép kiểu'], answer: 2, explanation: '=== so sánh cả giá trị lẫn kiểu dữ liệu mà không ép kiểu.' },
    { text: 'Sự kiện nào thường được dùng để phản hồi thao tác nhấn nút?', options: ['submit', 'change', 'click', 'load'], answer: 2, explanation: 'Sự kiện click được phát khi người dùng nhấn vào phần tử.' },
    { text: 'Promise.resolve(5) tạo ra trạng thái nào?', options: ['pending', 'fulfilled', 'rejected', 'cancelled'], answer: 1, explanation: 'Promise.resolve(value) tạo Promise đã hoàn thành thành công với value.' },
  ] },
  { id: 'programming-logic', title: 'Tư duy lập trình', subject: 'Lập trình', difficulty: 'Trung bình', duration: 15, description: 'Thuật toán, vòng lặp, độ phức tạp và tư duy giải quyết vấn đề.', questions: [
    { text: 'Cấu trúc nào lặp lại một khối lệnh khi điều kiện còn đúng?', options: ['if/else', 'while', 'switch', 'return'], answer: 1, explanation: 'while tiếp tục lặp khi điều kiện được đánh giá là đúng.' },
    { text: 'Độ phức tạp thời gian của tìm kiếm tuyến tính trên n phần tử là gì?', options: ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], answer: 2, explanation: 'Trong trường hợp xấu nhất, tìm kiếm tuyến tính kiểm tra n phần tử.' },
    { text: 'Điều kiện cần để tìm kiếm nhị phân hoạt động đúng trên mảng là gì?', options: ['Mảng có số phần tử chẵn', 'Mảng đã được sắp xếp', 'Mảng không có số âm', 'Mảng không trùng giá trị'], answer: 1, explanation: 'Tìm kiếm nhị phân dựa trên thứ tự đã sắp xếp để loại bỏ một nửa phạm vi.' },
    { text: 'Trong thuật toán, biến đếm thường được dùng để làm gì?', options: ['Đếm số lần lặp hoặc số phần tử', 'Sắp xếp dữ liệu tự động', 'Lưu toàn bộ chương trình', 'Dừng mọi hàm'], answer: 0, explanation: 'Biến đếm theo dõi số lần lặp hoặc số lượng phần tử đã xử lý.' },
    { text: 'Bước đầu tiên hợp lý khi giải một bài toán lập trình mới là gì?', options: ['Viết mã ngay', 'Hiểu đầu vào, đầu ra và yêu cầu', 'Chọn ngôn ngữ phức tạp nhất', 'Tối ưu trước khi có lời giải'], answer: 1, explanation: 'Xác định yêu cầu, dữ liệu đầu vào và kết quả mong muốn trước khi thiết kế lời giải.' },
  ] },
];

async function loadExamCatalog() {
  const response = await fetch('/api/quiz/exams', { credentials: 'same-origin' });
  const catalog = await response.json();
  if (!response.ok) throw new Error(catalog.error || 'Không thể tải danh sách đề thi.');
  return catalog.map((exam) => ({
    ...exam,
    questionCount: exam.questionCount || 0,
    isDraft: (exam.questionCount || 0) === 0,
  }));
}

let exams = [];

const historyKey = 'eduhubExamHistory';
const $ = (selector) => document.querySelector(selector);
const homeView = $('#examHome');
const sessionView = $('#examSession');
const resultView = $('#examResult');
let activeExam = null;
let answers = [];
let questionIndex = 0;
let timerId = null;
let secondsLeft = 0;
let startedAt = 0;
let resultData = null;
let submitting = false;
let activeAttemptId = null;

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
}

function readHistory() {
  try {
    const data = JSON.parse(localStorage.getItem(historyKey));
    return Array.isArray(data) ? data.slice(0, 3) : [];
  } catch {
    return [];
  }
}

function renderExams(subject = 'all') {
  const visible = subject === 'all' ? exams : exams.filter((exam) => exam.subject === subject);
  $('#examList').innerHTML = visible.map((exam, index) => `<article class="exam-card" style="animation-delay:${index * 55}ms"><div class="exam-card-top"><span class="subject-tag">${escapeHtml(exam.subject)}</span><span class="difficulty-tag">${exam.isDraft ? 'Chưa có câu hỏi' : escapeHtml(exam.difficulty)}</span></div><h3>${escapeHtml(exam.title)}</h3><p>${escapeHtml(exam.isDraft ? 'Đề thi đang chờ biên soạn câu hỏi.' : exam.description)}</p><div class="exam-card-foot"><span>${Number(exam.questionCount || exam.questions.length)} câu · ${exam.duration} phút</span><button class="text-button start-exam" type="button" data-exam-id="${escapeHtml(exam.id)}" ${exam.isDraft ? 'disabled title="Đề thi chưa có câu hỏi"' : ''}>${exam.isDraft ? 'Sắp mở' : 'Bắt đầu →'}</button></div></article>`).join('');
}

function renderHistory() {
  const history = readHistory();
  $('#historyCount').textContent = `${history.length} lượt thi`;
  $('#historyList').innerHTML = history.length ? history.slice(0, 5).map((item) => `<article class="history-row"><div class="history-name"><span class="history-mark">${escapeHtml(item.subject.slice(0, 1))}</span><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.subject)} · ${escapeHtml(item.date)}</small></span></div><span class="history-score">${item.score}%</span></article>`).join('') : '<p class="empty-history">Các lượt thi đã hoàn thành sẽ xuất hiện tại đây.</p>';
}

function showView(view) {
  homeView.classList.toggle('is-hidden', view !== 'home');
  sessionView.classList.toggle('is-hidden', view !== 'session');
  resultView.classList.toggle('is-hidden', view !== 'result');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function formatTime(seconds) {
  return `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
}

function renderTimer() {
  $('#timerValue').textContent = formatTime(secondsLeft);
  $('#examTimer').classList.toggle('is-urgent', secondsLeft <= 60);
}

function startTimer() {
  clearInterval(timerId);
  timerId = setInterval(() => {
    secondsLeft -= 1;
    renderTimer();
    if (secondsLeft <= 0) submitExam(true);
  }, 1000);
}

async function beginExam(exam) {
  try {
    const response = await fetch(`/api/quiz/exams/${encodeURIComponent(exam.id)}`, { credentials: 'same-origin' });
    const detail = await response.json();
    if (!response.ok) throw new Error(detail.error || 'Không thể tải đề thi.');
    exam = { ...exam, ...detail, questions: detail.questions };
  } catch (error) {
    alert(error.message);
    return;
  }
  activeExam = exam;
  answers = Array(exam.questions.length).fill(null);
  questionIndex = 0;
  secondsLeft = exam.duration * 60;
  startedAt = Date.now();
  resultData = null;
  activeAttemptId = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  $('#submitError').classList.add('is-hidden');
  $('#submitError').textContent = '';
  $('#sessionSubject').textContent = exam.subject.toUpperCase();
  $('#sessionTitle').textContent = exam.title;
  renderQuestion();
  renderTimer();
  showView('session');
  startTimer();
}

function renderQuestion() {
  const question = activeExam.questions[questionIndex];
  const answered = answers.filter((answer) => answer !== null).length;
  const percent = Math.round(answered / activeExam.questions.length * 100);
  $('#questionNumber').textContent = `CÂU ${String(questionIndex + 1).padStart(2, '0')}`;
  $('#questionProgress').textContent = `Câu ${questionIndex + 1} / ${activeExam.questions.length}`;
  $('#answeredProgress').textContent = `${answered} câu đã trả lời`;
  $('#railAnsweredCount').textContent = `${answered}/${activeExam.questions.length}`;
  $('.progress-track').setAttribute('aria-valuenow', String(percent));
  $('#progressBar').style.width = `${percent}%`;
  $('#questionText').textContent = question.text;
  if (question.type === 'essay') {
    $('#answerOptions').innerHTML = `<legend class="sr-only">Viết câu trả lời của bạn</legend><textarea id="essayAnswer" class="builder-answer-text" rows="8" placeholder="Nhập câu trả lời tự luận...">${escapeHtml(typeof answers[questionIndex] === 'string' ? answers[questionIndex] : '')}</textarea>`;
  } else if (question.type === 'multiple_choice') {
    const selected = Array.isArray(answers[questionIndex]) ? answers[questionIndex] : [];
    $('#answerOptions').innerHTML = `<legend class="sr-only">Chọn một hoặc nhiều đáp án</legend>${question.options.map((option, index) => `<label class="answer-option"><input type="checkbox" name="answer-multiple" value="${index}" ${selected.includes(index) ? 'checked' : ''}><span class="answer-letter">${String.fromCharCode(65 + index)}</span><span class="answer-copy">${escapeHtml(option)}</span></label>`).join('')}`;
  } else {
    $('#answerOptions').innerHTML = `<legend class="sr-only">Chọn đáp án của bạn</legend>${question.options.map((option, index) => `<label class="answer-option"><input type="radio" name="answer" value="${index}" ${answers[questionIndex] === index ? 'checked' : ''}><span class="answer-letter">${String.fromCharCode(65 + index)}</span><span class="answer-copy">${escapeHtml(option)}</span></label>`).join('')}`;
  }
  $('#questionNavigator').innerHTML = activeExam.questions.map((_, index) => {
    const answered = answers[index] !== null;
    const current = index === questionIndex;
    return `<button class="question-jump ${current ? 'is-current' : ''} ${answered ? 'is-answered' : ''}" type="button" data-question-index="${index}" aria-label="Câu ${index + 1}, ${answered ? 'đã trả lời' : 'chưa trả lời'}${current ? ', đang xem' : ''}" aria-current="${current ? 'step' : 'false'}">${index + 1}</button>`;
  }).join('');
  $('#previousQuestionBtn').disabled = questionIndex === 0;
  $('#nextQuestionBtn').disabled = questionIndex === activeExam.questions.length - 1;
}

async function submitExam(timedOut = false) {
  if (!activeExam || resultData || submitting) return;
  const unanswered = answers.filter((answer) => answer === null).length;
  if (!timedOut && unanswered && !confirm(`Bạn còn ${unanswered} câu chưa trả lời. Vẫn nộp bài?`)) return;
  if (!timedOut && !unanswered && !confirm('Nộp bài thi ngay bây giờ?')) return;
  clearInterval(timerId);
  const duration = Math.min(activeExam.duration * 60, Math.floor((Date.now() - startedAt) / 1000));
  submitting = true;
  $('#submitExamBtn').disabled = true;
  $('#submitError').classList.add('is-hidden');
  try {
    const answersPayload = Object.fromEntries(
      activeExam.questions.map((question, index) => [String(question.id), answers[index]])
    );
    const response = await fetch(`/api/quiz/exams/${encodeURIComponent(activeExam.id)}/submit`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '',
      },
      body: JSON.stringify({
        answers: answersPayload,
      }),
    });
    const saved = await response.json();
    if (!response.ok) throw new Error(saved.error || 'Không thể đồng bộ kết quả.');
    if (
      typeof saved.score !== 'number' ||
      !Number.isInteger(saved.correct_count) ||
      !Number.isInteger(saved.graded_count) ||
      !Array.isArray(saved.review) ||
      saved.review.length !== activeExam.questions.length ||
      !saved.answers ||
      typeof saved.answers !== 'object' ||
      Array.isArray(saved.answers)
    ) {
      throw new Error('Máy chủ trả về kết quả chấm bài không hợp lệ.');
    }
    answers = activeExam.questions.map((question) => (
      Object.prototype.hasOwnProperty.call(saved.answers, String(question.id))
        ? saved.answers[String(question.id)]
        : null
    ));
    const result = {
      examId: activeExam.id,
      attemptId: activeAttemptId,
      title: activeExam.title,
      subject: activeExam.subject,
      correct: saved.correct_count,
      total: saved.graded_count,
      score: saved.score,
      duration,
      date: new Intl.DateTimeFormat('vi-VN', { dateStyle: 'medium' }).format(new Date()),
    };
    resultData = result;
    try {
      const history = readHistory().filter((item) => item.attemptId !== result.attemptId);
      localStorage.setItem(historyKey, JSON.stringify([result, ...history].slice(0, 3)));
    } catch {
      alert('Không thể lưu lịch sử trên trình duyệt này. Kết quả đã được máy chủ ghi nhận.');
    }
    renderResult(result, timedOut, saved.review, saved.updated_existing);
    renderHistory();
    renderAnalytics();
    showView('result');
  } catch (error) {
    $('#submitError').textContent = `Không thể nộp bài: ${error.message} Câu trả lời vẫn được giữ trên trang; hãy khắc phục lỗi rồi thử nộp lại.`;
    $('#submitError').classList.remove('is-hidden');
    if (!timedOut && secondsLeft > 0) startTimer();
  } finally {
    submitting = false;
    $('#submitExamBtn').disabled = false;
  }
}

function renderResult(result, timedOut, review, updatedExisting = false) {
  $('#scorePercent').textContent = `${result.score}%`;
  $('#resultSubject').textContent = result.subject.toUpperCase();
  $('#resultHeading').textContent = timedOut ? 'Hết giờ làm bài' : 'Bài làm đã hoàn thành';
  $('#resultMessage').textContent = updatedExisting
    ? 'Kết quả lần làm này đã được lưu và cập nhật bài nộp mới nhất.'
    : (result.score >= 80
      ? 'Làm tốt lắm. Bạn đã nắm khá vững các kiến thức trong bộ đề này.'
      : 'Hãy xem lại phần giải thích dưới đây và thử sức thêm một lần nữa.');
  $('#correctCount').textContent = result.correct;
  $('#incorrectCount').textContent = result.total - result.correct;
  $('#resultDuration').textContent = formatTime(result.duration);
  const reviewByQuestionId = new Map(review.map((item) => [String(item.question_id), item]));
  $('#answerReview').innerHTML = activeExam.questions.map((question, index) => {
    const questionReview = reviewByQuestionId.get(String(question.id));
    const correct = questionReview.correct;
    const correctAnswers = questionReview.correct_answers;
    const selected = answers[index] === null || answers[index] === undefined
      ? 'Chưa chọn đáp án'
      : (question.type === 'essay'
        ? answers[index]
        : (Array.isArray(answers[index])
          ? answers[index].map((answer) => question.options[answer]).join(', ')
          : question.options[answers[index]]));
    const resultLine = question.type === 'essay'
      ? 'Chờ giáo viên chấm'
      : (correct ? '✓ Trả lời đúng' : '× Cần xem lại');
    const answerText = question.type === 'essay'
      ? 'Đáp án tự luận được ẩn; điểm sẽ được cập nhật sau khi giáo viên chấm.'
      : `Đáp án đúng: <strong>${escapeHtml(correctAnswers.map((answer) => question.options[answer]).join(', '))}</strong>`;
    return `<article class="review-item ${correct === null ? '' : (correct ? 'is-correct' : 'is-wrong')}"><div class="review-result-line"><span>${resultLine}</span><strong>Câu ${index + 1}</strong></div><h3>${escapeHtml(question.text)}</h3><p class="review-answer">Bạn chọn: <strong>${escapeHtml(selected)}</strong></p><p class="review-answer">${answerText}</p><p class="review-explanation">${escapeHtml(questionReview.explanation || '')}</p></article>`;
  }).join('');
}


function renderAnalytics() {
  const history = readHistory();
  const root = $('#analyticsContent');
  if (!root) return;

  if (!history.length) {
    root.innerHTML = '<p class="analytics-empty">Chưa có dữ liệu thống kê. Hãy hoàn thành một bài thi để xem biểu đồ của bạn.</p>';
    return;
  }

  const totalAttempts = history.length;
  const average = Math.round(history.reduce((sum, item) => sum + Number(item.score || 0), 0) / totalAttempts);
  const totalCorrect = history.reduce((sum, item) => sum + Number(item.correct || 0), 0);
  const totalQuestions = history.reduce((sum, item) => sum + Number(item.total || 0), 0);
  const totalWrong = Math.max(0, totalQuestions - totalCorrect);
  const correctPercent = totalQuestions ? Math.round(totalCorrect / totalQuestions * 100) : 0;
  const wrongPercent = totalQuestions ? 100 - correctPercent : 0;
  const chronological = [...history].reverse();
  const scoreLabel = (item) => `${escapeHtml(item.title || 'Bài thi')} · ${escapeHtml(item.date || '')}`;

  const bars = chronological.map((item, index) => {
    const score = Math.max(0, Math.min(100, Number(item.score) || 0));
    return `<div class="chart-bar-item" title="${scoreLabel(item)}: ${score}%"><div class="chart-bar-value">${score}%</div><div class="chart-bar-track"><span style="height:${score}%"></span></div><small>Lượt ${index + 1}</small></div>`;
  }).join('');

  const width = 560, height = 220, left = 34, right = 18, top = 20, bottom = 34;
  const plotWidth = width - left - right, plotHeight = height - top - bottom;
  const points = chronological.map((item, index) => {
    const x = chronological.length === 1 ? left + plotWidth / 2 : left + index * plotWidth / (chronological.length - 1);
    const score = Math.max(0, Math.min(100, Number(item.score) || 0));
    return { x, y: top + (100 - score) / 100 * plotHeight, score, index };
  });
  const polyline = points.map(point => `${point.x},${point.y}`).join(' ');
  const grid = [0, 25, 50, 75, 100].map(value => {
    const y = top + (100 - value) / 100 * plotHeight;
    return `<line x1="${left}" y1="${y}" x2="${width-right}" y2="${y}" class="chart-grid-line"/><text x="${left-8}" y="${y+4}" text-anchor="end" class="chart-axis-label">${value}</text>`;
  }).join('');
  const dots = points.map(point => `<circle cx="${point.x}" cy="${point.y}" r="4" class="chart-dot"><title>Lượt ${point.index + 1}: ${point.score}%</title></circle>`).join('');
  const xLabels = points.map(point => `<text x="${point.x}" y="${height-10}" text-anchor="middle" class="chart-axis-label">${point.index + 1}</text>`).join('');
  const maxBars = chronological.slice(-10);
  const visibleBars = maxBars.map((item, index) => {
    const score = Math.max(0, Math.min(100, Number(item.score) || 0));
    const attemptNumber = chronological.length - maxBars.length + index + 1;
    return `<div class="chart-bar-item" title="${scoreLabel(item)}: ${score}%"><div class="chart-bar-value">${score}%</div><div class="chart-bar-track"><span style="height:${score}%"></span></div><small>Lượt ${attemptNumber}</small></div>`;
  }).join('');

  root.innerHTML = `
    <div class="analytics-metrics">
      <article class="analytics-metric"><span>Tổng lượt thi</span><strong>${totalAttempts}</strong><small>Các lượt đã lưu</small></article>
      <article class="analytics-metric"><span>Điểm trung bình</span><strong>${average}%</strong><small>Trên thang điểm 100</small></article>
      <article class="analytics-metric"><span>Tổng câu đúng</span><strong>${totalCorrect}</strong><small>Qua tất cả lượt thi</small></article>
      <article class="analytics-metric"><span>Tổng câu chưa đúng</span><strong>${totalWrong}</strong><small>Qua tất cả lượt thi</small></article>
    </div>
    <div class="analytics-chart-grid">
      <article class="analytics-card"><div class="analytics-card-heading"><div><h3>Tỷ lệ câu đúng và chưa đúng</h3><p>Tổng hợp từ các lượt thi đã lưu</p></div></div>
        <div class="donut-layout"><div class="donut-chart" style="--correct-angle:${correctPercent * 3.6}deg"><div><strong>${correctPercent}%</strong><span>câu đúng</span></div></div><div class="chart-legend"><span><i class="legend-correct"></i>Đúng <strong>${totalCorrect}</strong> (${correctPercent}%)</span><span><i class="legend-wrong"></i>Chưa đúng <strong>${totalWrong}</strong> (${wrongPercent}%)</span></div></div>
      </article>
      <article class="analytics-card"><div class="analytics-card-heading"><div><h3>Điểm theo từng lượt thi</h3><p>Hiển thị tối đa 10 lượt gần nhất</p></div></div><div class="bar-chart">${visibleBars}</div></article>
      <article class="analytics-card analytics-card-wide"><div class="analytics-card-heading"><div><h3>Xu hướng điểm số</h3><p>Điểm thay đổi qua các lần làm bài theo thứ tự thời gian</p></div></div>
        <div class="line-chart-wrap"><svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Biểu đồ đường thể hiện điểm số theo lượt thi">${grid}<polyline points="${polyline}" class="chart-line"/>${dots}${xLabels}</svg></div><p class="chart-footnote">Trục ngang: lượt thi · Trục dọc: điểm số (%)</p>
      </article>
    </div>`;
}

$('#examFilters').addEventListener('click', (event) => {
  const button = event.target.closest('[data-filter]');
  if (!button) return;
  $('#examFilters').querySelectorAll('[data-filter]').forEach((tab) => {
    tab.classList.toggle('active', tab === button);
    tab.setAttribute('aria-pressed', String(tab === button));
  });
  renderExams(button.dataset.filter);
});

$('#examList').addEventListener('click', (event) => {
  const button = event.target.closest('.start-exam');
  const exam = exams.find((item) => item.id === button?.dataset.examId);
  if (exam) beginExam(exam);
});

$('#answerOptions').addEventListener('change', (event) => {
  if (event.target.matches('input[name="answer"]')) {
    answers[questionIndex] = Number(event.target.value);
    renderQuestion();
  } else if (event.target.matches('input[name="answer-multiple"]')) {
    const selected = Array.isArray(answers[questionIndex]) ? [...answers[questionIndex]] : [];
    const value = Number(event.target.value);
    if (event.target.checked && !selected.includes(value)) selected.push(value);
    if (!event.target.checked) selected.splice(selected.indexOf(value), 1);
    answers[questionIndex] = selected.length ? selected : null;
    renderQuestion();
  }
});
$('#answerOptions').addEventListener('input', (event) => {
  if (event.target.matches('#essayAnswer')) {
    answers[questionIndex] = event.target.value.trim() ? event.target.value : null;
  }
});

$('#questionNavigator').addEventListener('click', (event) => {
  const button = event.target.closest('[data-question-index]');
  if (button) { questionIndex = Number(button.dataset.questionIndex); renderQuestion(); }
});

$('#previousQuestionBtn').addEventListener('click', () => { if (questionIndex > 0) { questionIndex -= 1; renderQuestion(); } });
$('#nextQuestionBtn').addEventListener('click', () => { if (questionIndex < activeExam.questions.length - 1) { questionIndex += 1; renderQuestion(); } });
$('#submitExamBtn').addEventListener('click', () => submitExam());
$('#exitExamBtn').addEventListener('click', () => {
  if (confirm('Thoát bài thi? Các câu trả lời hiện tại sẽ không được lưu.')) { clearInterval(timerId); activeExam = null; showView('home'); }
});
$('#resultHomeBtn').addEventListener('click', () => { activeExam = null; showView('home'); });
$('#retryExamBtn').addEventListener('click', () => {
  const exam = exams.find((item) => item.id === resultData?.examId);
  if (exam) beginExam(exam);
});

async function initializeQuiz() {
  try {
    exams = await loadExamCatalog();
  } catch (error) {
    $('#examList').innerHTML = `<p class="analytics-empty">${escapeHtml(error.message)}</p>`;
  }
  renderExams();
  renderHistory();
  renderAnalytics();
}

initializeQuiz();