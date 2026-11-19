const catalogStorageKey = 'eduhubExamCatalog';
const defaultExams = [
  { id: 'html-foundations', title: 'Nền tảng HTML & CSS', subject: 'HTML & CSS', questionCount: 5, duration: 12, description: 'Cấu trúc trang, semantic HTML và các nguyên tắc CSS.' },
  { id: 'javascript-basics', title: 'JavaScript căn bản', subject: 'JavaScript', questionCount: 6, duration: 15, description: 'Biến, kiểu dữ liệu, hàm và các thao tác với mảng.' },
  { id: 'programming-logic', title: 'Tư duy lập trình', subject: 'Lập trình', questionCount: 5, duration: 15, description: 'Thuật toán, vòng lặp, độ phức tạp và tư duy giải quyết vấn đề.' },
];
const knownExamIds = new Set(defaultExams.map((exam) => exam.id));
const examTableBody = document.getElementById('examTableBody');
const examForm = document.getElementById('examForm');
const examDialog = document.getElementById('examDialog');
let exams = [];
let builderQuestions = [];
let editorExamId = null;
let publishAfterSave = false;

async function renderQuizAnalytics() {
  const status = document.getElementById('quizAnalyticsStatus');
  const metrics = document.getElementById('quizAnalyticsMetrics');
  const examStats = document.getElementById('quizExamStats');
  const recentAttempts = document.getElementById('quizRecentAttempts');
  if (!status || !metrics || !examStats || !recentAttempts) return;

  status.textContent = 'Đang tải số liệu...';
  try {
    const response = await fetch('/api/admin/quiz/statistics', { credentials: 'same-origin' });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Không thể tải thống kê.');
    const summary = data.summary;
    const accuracy = summary.total_questions
      ? Math.round(summary.correct_count / summary.total_questions * 100)
      : 0;
    const metricItems = [
      ['Tổng lượt thi', summary.attempts, 'Đã nộp trên hệ thống'],
      ['Điểm trung bình', `${summary.average_score}%`, 'Trên thang điểm 100'],
      ['Tài khoản có lượt thi', summary.learners, 'Chỉ dữ liệu chi tiết còn lưu'],
      ['Tỷ lệ câu đúng', `${accuracy}%`, 'Tính trên mọi lượt thi'],
    ];
    metrics.innerHTML = metricItems.map(([label, value, caption]) => `
      <article class="analytics-metric"><span>${label}</span><strong>${value}</strong><small>${caption}</small></article>
    `).join('');

    status.textContent = summary.attempts ? `Đã ghi nhận ${summary.attempts} lượt nộp bài.` : 'Chưa có lượt nộp bài nào trên hệ thống.';
    examStats.innerHTML = data.exams.length ? data.exams.map((exam) => `
      <article class="exam-stat-row">
        <div class="exam-stat-copy"><strong>${escapeHtml(exam.exam_title)}</strong><small>${escapeHtml(exam.subject)} · ${exam.attempts} lượt · cao nhất ${exam.best_score}%</small></div>
        <div class="exam-stat-score"><span>${exam.average_score}%</span><div class="exam-stat-track"><i style="width:${Math.max(0, Math.min(100, Number(exam.average_score) || 0))}%"></i></div></div>
      </article>
    `).join('') : '<p class="analytics-empty">Chưa có dữ liệu theo đề thi.</p>';

    recentAttempts.innerHTML = data.recent.length ? data.recent.map((attempt) => `
      <tr><td>${escapeHtml(attempt.learner)}</td><td>${escapeHtml(attempt.exam_title)}<small class="attempt-subject">${escapeHtml(attempt.subject)}</small></td><td><strong>${attempt.score}%</strong><small class="attempt-subject">${attempt.correct_count}/${attempt.total_questions} câu</small></td><td>${escapeHtml(attempt.created_at)}</td></tr>
    `).join('') : '<tr class="empty-row"><td colspan="4">Chưa có lượt nộp bài.</td></tr>';
  } catch (error) {
    status.textContent = error.message;
    metrics.replaceChildren();
    examStats.innerHTML = '';
    recentAttempts.innerHTML = '<tr class="empty-row"><td colspan="4">Không tải được dữ liệu.</td></tr>';
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
}

async function loadExams() {
  const response = await fetch('/api/admin/quiz/exams', { credentials: 'same-origin' });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Không thể tải danh sách đề thi.');
  return data;
}

function showFeedback(message, isError = false) {
  const feedback = document.getElementById('catalogFeedback');
  feedback.textContent = message;
  feedback.classList.toggle('is-error', isError);
}

function getVisibleExams() {
  const query = document.getElementById('examSearch').value.trim().toLocaleLowerCase('vi');
  const subject = document.getElementById('subjectFilter').value;
  return exams.filter((exam) => {
    const matchesQuery = `${exam.title} ${exam.subject}`.toLocaleLowerCase('vi').includes(query);
    const matchesSubject = subject === 'all' || (subject === 'other'
      ? !['HTML & CSS', 'JavaScript', 'Lập trình'].includes(exam.subject)
      : exam.subject === subject);
    return matchesQuery && matchesSubject;
  });
}

function renderExams() {
  const visibleExams = getVisibleExams();
  document.getElementById('examCount').textContent = `${exams.length} đề thi`;

  if (!visibleExams.length) {
    examTableBody.innerHTML = '<tr class="empty-row"><td colspan="6">Không tìm thấy đề thi phù hợp.</td></tr>';
    return;
  }

  examTableBody.innerHTML = visibleExams.map((exam) => {
    const isQuestionBanked = (exam.questions?.length || 0) > 0;
    const statusLabel = exam.status === 'published' ? 'Đã xuất bản' : (isQuestionBanked ? 'Bản nháp · Có câu hỏi' : 'Bản nháp');
    return `
      <tr>
        <td class="exam-title-cell"><strong>${escapeHtml(exam.title)}</strong><small>${escapeHtml(exam.description || 'Đề thi mới')}</small></td>
        <td><span class="subject-label">${escapeHtml(exam.subject)}</span></td>
        <td>${Number(exam.questionCount)} câu</td>
        <td>${Number(exam.duration)} phút</td>
        <td><span class="status-label ${exam.status === 'published' ? '' : 'draft'}">${statusLabel}</span></td>
        <td><div class="row-actions">
          <button class="icon-button manage-questions" type="button" data-id="${escapeHtml(exam.id)}" aria-label="Quản lý câu hỏi đề ${escapeHtml(exam.title)}" title="Quản lý câu hỏi">?</button>
          ${exam.status !== 'published' ? `<button class="icon-button publish-exam" type="button" data-id="${escapeHtml(exam.id)}" aria-label="Xuất bản đề ${escapeHtml(exam.title)}" title="Xuất bản và giao">↗</button>` : ''}
          <button class="icon-button edit-exam" type="button" data-id="${escapeHtml(exam.id)}" aria-label="Sửa đề ${escapeHtml(exam.title)}" title="Sửa đề">✎</button>
          <button class="icon-button delete delete-exam" type="button" data-id="${escapeHtml(exam.id)}" aria-label="Xóa đề ${escapeHtml(exam.title)}" title="Xóa đề">×</button>
        </div></td>
      </tr>`;
  }).join('');
}

function renderBuilder() {
  const root = document.getElementById('builderQuestions');
  if (!root) return;
  root.innerHTML = builderQuestions.length ? builderQuestions.map((question, index) => `
    <article class="builder-question" data-builder-index="${index}">
      <header class="builder-card-toolbar">
        <span class="builder-question-number">Câu ${String(index + 1).padStart(2, '0')}</span>
        <select class="builder-type" aria-label="Loại câu hỏi ${index + 1}">
          <option value="single_choice" ${question.type === 'single_choice' ? 'selected' : ''}>Trắc nghiệm</option>
          <option value="multiple_choice" ${question.type === 'multiple_choice' ? 'selected' : ''}>Hộp kiểm</option>
          <option value="true_false" ${question.type === 'true_false' ? 'selected' : ''}>Đúng / Sai</option>
          <option value="essay" ${question.type === 'essay' ? 'selected' : ''}>Trả lời ngắn / Tự luận</option>
        </select>
        <label class="builder-points-wrap"><input class="builder-points" type="number" min="1" max="100" value="${Number(question.points || 1)}" aria-label="Điểm câu ${index + 1}"><span>điểm</span></label>
      </header>
      <div class="quiz-question-stage">
        <span class="quiz-stage-label">NỘI DUNG CÂU HỎI</span>
        <textarea class="builder-text" rows="2" placeholder="Nhập câu hỏi tại đây..." aria-label="Nội dung câu hỏi ${index + 1}">${escapeHtml(question.text || '')}</textarea>
      </div>
      <p class="builder-answer-heading">${question.type === 'essay' ? 'ĐÁP ÁN MẪU' : 'CHỌN ĐÁP ÁN ĐÚNG'}</p>
      <div class="builder-options ${question.type === 'essay' ? 'is-hidden' : ''}">
        ${(question.type === 'true_false' ? ['Sai', 'Đúng'] : (question.options?.length ? question.options : ['', '', '', ''])).map((option, optionIndex) => {
          const correct = question.type === 'multiple_choice'
            ? (question.answers || []).includes(optionIndex)
            : Number(question.answer ?? 0) === optionIndex;
          const inputType = question.type === 'multiple_choice' ? 'checkbox' : 'radio';
          return `<div class="builder-option-row answer-tile answer-tile-${optionIndex % 4}">
            <input class="builder-correct" type="${inputType}" name="correct-${index}" value="${optionIndex}" ${correct ? 'checked' : ''} aria-label="Đánh dấu đáp án đúng">
            <input class="builder-option-text" type="text" value="${escapeHtml(option)}" placeholder="Lựa chọn ${optionIndex + 1}" aria-label="Lựa chọn ${optionIndex + 1}" ${question.type === 'true_false' ? 'readonly' : ''}>
            ${question.type !== 'true_false' ? `<button type="button" class="builder-remove-option" data-option-index="${optionIndex}" aria-label="Xóa tùy chọn">×</button>` : ''}
          </div>`;
        }).join('')}
        ${question.type !== 'true_false' ? '<button type="button" class="builder-add-option">＋ Thêm lựa chọn</button>' : ''}
      </div>
      <label class="builder-answer-key-wrap ${question.type === 'essay' ? '' : 'is-hidden'}"><span>Đáp án mẫu để tự chấm <small>· Chỉ giáo viên xem được</small></span><textarea class="builder-answer-key" rows="3" placeholder="Nhập đáp án chuẩn">${escapeHtml(question.answer_key || '')}</textarea></label>
      <div class="builder-question-footer">
        <span class="builder-correct-hint">${question.type === 'essay' ? 'Đáp án mẫu được giữ kín với học sinh.' : 'Đáp án đúng được ẩn khi học sinh làm bài.'}</span>
        <button type="button" class="builder-duplicate-question" aria-label="Nhân bản câu hỏi">▢</button>
        <button type="button" class="remove-builder-question" data-index="${index}" aria-label="Xóa câu hỏi">×</button>
        <label class="builder-required"><span>Bắt buộc</span><input type="checkbox" class="builder-required-input" ${question.required === false ? '' : 'checked'}></label>
      </div>
    </article>
  `).join('') : '<p class="analytics-empty">Chưa có câu hỏi. Nhấn “Thêm câu hỏi” để bắt đầu.</p>';
}

function openDialog(exam = null) {
  const isEditing = Boolean(exam);
  editorExamId = exam?.id || null;
  document.getElementById('examTitle').placeholder = isEditing ? 'Tên đề thi' : 'Tên đề thi mới';
  document.getElementById('examTitle').value = exam?.title || '';
  document.getElementById('examSubject').value = exam?.subject || '';
  document.getElementById('examDescription').value = exam?.description || '';
  document.getElementById('examDuration').value = exam?.duration ?? 15;
  document.getElementById('examStatus').value = exam?.status || 'draft';
  document.getElementById('examDueAt').value = exam?.due_at ? exam.due_at.slice(0, 16) : '';
  document.getElementById('examShuffle').checked = Boolean(exam?.shuffle_questions);
  builderQuestions = exam?.questions ? exam.questions.map((question) => ({ ...question })) : [{
    text: '',
    type: 'single_choice',
    options: ['', '', '', ''],
    answer: 0,
    answers: [],
    answer_key: '',
    points: 1,
  }];
  renderBuilder();
  renderSubmissions(exam?.id);
  examForm.dataset.editingId = exam?.id || '';
  examDialog.classList.remove('is-hidden');
  examDialog.setAttribute('aria-hidden', 'false');
  document.body.classList.add('quiz-editor-open');
  document.getElementById('examTitle').focus();
}

function closeDialog() {
  examDialog.classList.add('is-hidden');
  examDialog.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('quiz-editor-open');
  examForm.reset();
  editorExamId = null;
  delete examForm.dataset.editingId;
}

function collectBuilderQuestions() {
  return [...document.querySelectorAll('.builder-question')].map((card) => {
    const type = card.querySelector('.builder-type').value;
    const indexedOptions = type === 'essay'
      ? []
      : [...card.querySelectorAll('.builder-option-text')]
        .map((input, index) => ({ index, text: input.value.trim() }))
        .filter((option) => option.text);
    const options = indexedOptions.map((option) => option.text);
    const selectedOptionIndexes = [...card.querySelectorAll('.builder-correct:checked')]
      .map((input) => Number(input.value))
      .filter((value) => Number.isInteger(value));
    const correctValues = selectedOptionIndexes
      .map((selectedIndex) => indexedOptions.findIndex((option) => option.index === selectedIndex))
      .filter((index) => index >= 0);
    const question = builderQuestions[Number(card.dataset.builderIndex)] || {};
    return {
      id: question.id,
      text: card.querySelector('.builder-text').value.trim(),
      type,
      options,
      answer: type === 'multiple_choice' || type === 'essay' ? -1 : (correctValues[0] ?? 0),
      answers: type === 'multiple_choice' ? correctValues : [],
      answer_key: card.querySelector('.builder-answer-key').value.trim(),
      points: Number(card.querySelector('.builder-points').value),
      required: card.querySelector('.builder-required-input').checked,
      explanation: question.explanation || '',
    };
  });
}

function updateBuilderFromDom() {
  builderQuestions = collectBuilderQuestions();
}

async function renderSubmissions(examId) {
  const root = document.getElementById('submissionList');
  const summary = document.getElementById('responseSummary');
  if (!root || !examId) {
    if (summary) summary.textContent = 'Lưu đề thi để xem bài nộp.';
    if (root) root.innerHTML = '<p class="quiz-empty">Lưu đề thi trước để xem bài làm được gửi.</p>';
    return;
  }
  try {
    const response = await fetch(`/api/admin/quiz/exams/${encodeURIComponent(examId)}/submissions`, { credentials: 'same-origin' });
    const submissions = await response.json();
    if (!response.ok) throw new Error(submissions.error || 'Không thể tải câu trả lời.');
    summary.textContent = `${submissions.length} bài làm đã nộp`;
    root.innerHTML = submissions.length ? submissions.map((submission) => `
      <article class="quiz-response-card">
        <strong>${escapeHtml(submission.name)}</strong>
        <span>${escapeHtml(submission.email)} · ${escapeHtml(submission.submitted_at || '')}</span>
        <p>Điểm tự động: ${Number(submission.auto_score)} · Trạng thái: ${escapeHtml(submission.status)}</p>
        ${Object.entries(submission.answers).map(([questionId, answer]) => `<p><b>Câu ${escapeHtml(questionId)}:</b> ${escapeHtml(Array.isArray(answer) ? answer.join(', ') : answer)}</p>`).join('')}
        <label class="form-field"><span>Điểm cộng tự luận</span><input class="manual-grade" type="number" min="0" value="${Number(submission.manual_score || 0)}" data-id="${submission.id}"></label>
        <label class="form-field"><span>Nhận xét</span><textarea class="grade-comment" rows="2" data-id="${submission.id}">${escapeHtml(submission.teacher_comment || '')}</textarea></label>
        <button type="button" class="secondary-button save-grade" data-id="${submission.id}">Lưu điểm và nhận xét</button>
      </article>
    `).join('') : '<p class="quiz-empty">Chưa có học sinh nào nộp bài.</p>';
  } catch (error) {
    summary.textContent = 'Không thể tải bài nộp.';
    root.innerHTML = `<p class="quiz-empty">${escapeHtml(error.message)}</p>`;
  }
}

async function handleSubmit(event) {
  event.preventDefault();
  if (!examForm.reportValidity()) return;

  const editingId = examForm.dataset.editingId;
  const previous = exams.find((exam) => exam.id === editingId);
  const exam = {
    title: document.getElementById('examTitle').value.trim(),
    subject: document.getElementById('examSubject').value.trim(),
    duration: Number(document.getElementById('examDuration').value),
    description: document.getElementById('examDescription').value.trim(),
    status: document.getElementById('examStatus').value,
    due_at: document.getElementById('examDueAt').value || null,
    shuffle_questions: document.getElementById('examShuffle').checked,
  };

  if (!exam.title || !exam.subject || !Number.isInteger(exam.duration) || exam.duration < 1) return;
  const questions = collectBuilderQuestions().filter((question) => question.text);
  if (!questions.length) {
    showFeedback('Hãy thêm ít nhất một câu hỏi cho đề thi.', true);
    return;
  }

  try {
    const response = await fetch(editingId ? `/api/admin/quiz/exams/${encodeURIComponent(editingId)}` : '/api/admin/quiz/exams', {
      method: editingId ? 'PUT' : 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '' },
      body: JSON.stringify(exam),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Không thể lưu đề thi.');
    const examId = editingId || data.id;
    const savedQuestionIds = questions.map((question) => question.id).filter(Boolean);
    for (const oldQuestion of previous?.questions || []) {
      if (oldQuestion.id && !savedQuestionIds.includes(oldQuestion.id)) {
        const deleteResponse = await fetch(
          `/api/admin/quiz/exams/${encodeURIComponent(examId)}/questions/${oldQuestion.id}`,
          {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: { 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '' },
          }
        );
        if (!deleteResponse.ok) throw new Error('Không thể xóa câu hỏi đã bỏ khỏi đề.');
      }
    }
    for (const question of questions) {
      const questionResponse = await fetch(
        question.id
          ? `/api/admin/quiz/exams/${encodeURIComponent(examId)}/questions/${question.id}`
          : `/api/admin/quiz/exams/${encodeURIComponent(examId)}/questions`,
        {
          method: question.id ? 'PUT' : 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '' },
          body: JSON.stringify(question),
        }
      );
      const questionData = await questionResponse.json();
      if (!questionResponse.ok) throw new Error(questionData.error || 'Không thể lưu câu hỏi.');
    }
    if (exam.status === 'published') {
      const publishResponse = await fetch(`/api/admin/quiz/exams/${encodeURIComponent(data.id)}/publish`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '' },
        body: JSON.stringify({ due_at: exam.due_at || null, student_ids: null }),
      });
      const publishData = await publishResponse.json();
      if (!publishResponse.ok) throw new Error(publishData.error || 'Đề chưa có câu hỏi nên không thể xuất bản.');
    }
    exams = await loadExams();
    renderExams();
    editorExamId = examId;
    examForm.dataset.editingId = examId;
    document.getElementById('saveState').textContent = exam.status === 'published' ? 'Đã xuất bản' : 'Đã lưu';
    await renderSubmissions(examId);
    if (publishAfterSave) {
      publishAfterSave = false;
      closeDialog();
    }
    showFeedback(exam.status === 'published' ? 'Đã lưu và xuất bản đề thi.' : (editingId ? 'Đã cập nhật đề thi.' : 'Đã tạo bản nháp.'));
  } catch (error) {
    publishAfterSave = false;
    showFeedback(error.message, true);
  }
}

async function deleteExam(id) {
  const exam = exams.find((item) => item.id === id);
  if (!exam || !confirm(`Bạn có chắc muốn xóa đề "${exam.title}" không?`)) return;
  try {
    const response = await fetch(`/api/admin/quiz/exams/${encodeURIComponent(id)}`, {
      method: 'DELETE',
      credentials: 'same-origin',
      headers: { 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '' },
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Không thể xóa đề thi.');
    exams = await loadExams();
    renderExams();
    showFeedback(`Đã xóa đề "${exam.title}".`);
  } catch (error) {
    showFeedback(error.message, true);
  }
}

async function publishExam(id) {
  const exam = exams.find((item) => item.id === id);
  if (!exam || !confirm(`Xuất bản và giao đề "${exam.title}" cho tất cả học sinh?`)) return;
  try {
    const response = await fetch(`/api/admin/quiz/exams/${encodeURIComponent(id)}/publish`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '' },
      body: JSON.stringify({ due_at: exam.due_at || null, student_ids: null }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Không thể xuất bản đề thi.');
    exams = await loadExams();
    renderExams();
    showFeedback(`Đã xuất bản và giao đề "${exam.title}" cho học sinh.`);
  } catch (error) {
    showFeedback(error.message, true);
  }
}

async function manageQuestions(id) {
  const exam = exams.find((item) => item.id === id);
  if (!exam) return;
  const action = window.prompt('Nhập thao tác: add, edit hoặc delete');
  if (!action) return;
  const normalized = action.trim().toLowerCase();
  try {
    if (normalized === 'delete') {
      const questionId = Number(window.prompt('Nhập ID câu hỏi cần xóa'));
      if (!Number.isInteger(questionId)) return;
      const response = await fetch(`/api/admin/quiz/exams/${encodeURIComponent(id)}/questions/${questionId}`, {
        method: 'DELETE',
        credentials: 'same-origin',
        headers: { 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '' },
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Không thể xóa câu hỏi.');
    } else if (normalized === 'add' || normalized === 'edit') {
      let questionId = null;
      if (normalized === 'edit') {
        questionId = Number(window.prompt('Nhập ID câu hỏi cần sửa'));
        if (!Number.isInteger(questionId)) return;
      }
      const payloadText = window.prompt('Nhập JSON câu hỏi', JSON.stringify({
        text: 'Nội dung câu hỏi',
        type: 'single_choice',
        options: ['Đáp án A', 'Đáp án B'],
        answer: 0,
        answers: [0],
        points: 1,
        explanation: '',
      }, null, 2));
      if (!payloadText) return;
      const payload = JSON.parse(payloadText);
      const response = await fetch(
        normalized === 'edit'
          ? `/api/admin/quiz/exams/${encodeURIComponent(id)}/questions/${questionId}`
          : `/api/admin/quiz/exams/${encodeURIComponent(id)}/questions`,
        {
          method: normalized === 'edit' ? 'PUT' : 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '' },
          body: JSON.stringify(payload),
        }
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Không thể lưu câu hỏi.');
    } else {
      throw new Error('Thao tác quản lý câu hỏi không hợp lệ.');
    }
    exams = await loadExams();
    renderExams();
    showFeedback('Đã cập nhật ngân hàng câu hỏi.');
  } catch (error) {
    showFeedback(error.message, true);
  }
}

document.getElementById('addExamBtn').addEventListener('click', () => openDialog());
document.getElementById('addBuilderQuestion').addEventListener('click', () => {
  updateBuilderFromDom();
  builderQuestions.push({
    text: '',
    type: 'single_choice',
    options: ['', '', '', ''],
    answer: 0,
    answers: [],
    answer_key: '',
    points: 1,
  });
  renderBuilder();
});
document.getElementById('closeDialogBtn').addEventListener('click', closeDialog);
document.querySelectorAll('[data-editor-jump]').forEach((button) => button.addEventListener('click', () => {
  document.getElementById(button.dataset.editorJump)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}));
document.getElementById('builderQuestions').addEventListener('click', (event) => {
  const button = event.target.closest('.remove-builder-question');
  const card = event.target.closest('.builder-question');
  if (!card) return;
  updateBuilderFromDom();
  const index = Number(card.dataset.builderIndex);
  if (button) {
    builderQuestions.splice(index, 1);
    renderBuilder();
    return;
  }
  if (event.target.closest('.builder-add-option')) {
    builderQuestions[index].options.push('');
  } else if (event.target.closest('.builder-remove-option')) {
    const optionIndex = Number(event.target.closest('.builder-remove-option').dataset.optionIndex);
    const removed = builderQuestions[index].options.splice(optionIndex, 1);
    if (builderQuestions[index].type === 'multiple_choice') {
      builderQuestions[index].answers = (builderQuestions[index].answers || [])
        .filter((answer) => answer !== optionIndex)
        .map((answer) => answer > optionIndex ? answer - 1 : answer);
    } else if (builderQuestions[index].answer === optionIndex) {
      builderQuestions[index].answer = 0;
    } else if (builderQuestions[index].answer > optionIndex) {
      builderQuestions[index].answer -= 1;
    }
    if (!removed.length) return;
  } else if (event.target.closest('.builder-duplicate-question')) {
    const duplicate = { ...builderQuestions[index] };
    delete duplicate.id;
    builderQuestions.splice(index + 1, 0, duplicate);
  } else {
    return;
  }
  renderBuilder();
});
document.getElementById('builderQuestions').addEventListener('change', (event) => {
  if (!event.target.matches('.builder-type')) return;
  const card = event.target.closest('.builder-question');
  const index = Number(card.dataset.builderIndex);
  updateBuilderFromDom();
  const question = builderQuestions[index];
  if (question.type !== 'essay' && !question.options.length) {
    question.options = question.type === 'true_false' ? ['Sai', 'Đúng'] : ['Tùy chọn 1', 'Tùy chọn 2'];
  }
  if (question.type === 'true_false') question.options = ['Sai', 'Đúng'];
  renderBuilder();
});
document.getElementById('examTitle').addEventListener('input', (event) => {
  document.getElementById('saveState').textContent = 'Chưa lưu';
});
document.getElementById('saveExamBtn').addEventListener('click', () => {
  publishAfterSave = false;
  document.getElementById('examStatus').value = 'draft';
  examForm.requestSubmit();
});
document.getElementById('publishExamBtn').addEventListener('click', () => {
  publishAfterSave = true;
  document.getElementById('examStatus').value = 'published';
  examForm.requestSubmit();
});
document.getElementById('previewExamBtn').addEventListener('click', () => {
  window.open('/quiz.html', '_blank', 'noopener');
});
document.getElementById('submissionList').addEventListener('click', async (event) => {
  const button = event.target.closest('.save-grade');
  if (!button) return;
  const id = button.dataset.id;
  const card = button.closest('.quiz-response-card');
  try {
    const response = await fetch(`/api/admin/quiz/submissions/${id}/grade`, {
      method: 'PUT',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || '' },
      body: JSON.stringify({
        manual_score: Number(card.querySelector('.manual-grade').value),
        comment: card.querySelector('.grade-comment').value,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Không thể lưu điểm.');
    showFeedback('Đã lưu điểm và nhận xét.');
    await renderSubmissions(editorExamId);
  } catch (error) {
    showFeedback(error.message, true);
  }
});
examForm.addEventListener('submit', handleSubmit);
examTableBody.addEventListener('click', (event) => {
  const editButton = event.target.closest('.edit-exam');
  const deleteButton = event.target.closest('.delete-exam');
  const manageButton = event.target.closest('.manage-questions');
  const publishButton = event.target.closest('.publish-exam');
  if (editButton) openDialog(exams.find((exam) => exam.id === editButton.dataset.id));
  if (deleteButton) deleteExam(deleteButton.dataset.id);
  if (manageButton) manageQuestions(manageButton.dataset.id);
  if (publishButton) publishExam(publishButton.dataset.id);
});
document.getElementById('examSearch').addEventListener('input', renderExams);
document.getElementById('subjectFilter').addEventListener('change', renderExams);
document.getElementById('refreshQuizAnalytics').addEventListener('click', renderQuizAnalytics);
examDialog.addEventListener('click', (event) => { if (event.target === examDialog) closeDialog(); });
document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !examDialog.classList.contains('is-hidden')) closeDialog(); });

async function initializeExamAdmin() {
  try {
    exams = await loadExams();
  } catch (error) {
    showFeedback(error.message, true);
  }
  renderExams();
  renderQuizAnalytics();
}

initializeExamAdmin();