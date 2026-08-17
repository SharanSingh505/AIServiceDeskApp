const ticketList = document.querySelector('#ticket-list');
const result = document.querySelector('#result');
const ticketForm = document.querySelector('#create-ticket-form');
const formStatus = document.querySelector('#form-status');
let activeTicketId = null;
let activeEngineerId = null;

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
}

async function showRecommendation(ticketId) {
  result.innerHTML = '<p>Calculating recommendation…</p>';
  const response = await fetch(`/api/tickets/${ticketId}/recommendation`);
  const data = await response.json();
  renderRecommendation(data);
}

function renderRecommendation(data) {
  const r = data.recommendation;
  activeTicketId = data.ticket_id || data.ticket.id;
  activeEngineerId = r.engineer_id;
  result.innerHTML = `
    <p class="eyebrow">RECOMMENDATION FOR ${escapeHtml(data.ticket_id)}</p>
    <h2>${escapeHtml(r.engineer_name)}</h2><p>${escapeHtml(r.team)}</p>
    <div class="score">${r.total_score}<span>/100 score</span></div>
    <dl><dt>Predicted resolution</dt><dd>${r.predicted_resolution_hours} hours</dd>
    <dt>SLA target</dt><dd>${r.sla_target_hours} hours</dd>
    <dt>SLA likelihood</dt><dd class="${r.likely_to_meet_sla ? 'good' : 'risk'}">${r.likely_to_meet_sla ? 'Likely to meet' : 'At risk'}</dd></dl>
    <p class="reason">${escapeHtml(r.reason)}</p><button id="approve-assignment" class="approve">Approve & assign to ${escapeHtml(r.engineer_name)}</button><p class="notice">${escapeHtml(data.decision_note)}</p>`;
  document.querySelector('#approve-assignment').addEventListener('click', approveAssignment);
}

async function approveAssignment() {
  const response = await fetch(`/api/tickets/${activeTicketId}/assign?engineer_id=${activeEngineerId}`, { method: 'POST' });
  const data = await response.json();
  result.innerHTML += `<p class="assigned">✓ ${escapeHtml(data.message)}</p>`;
  document.querySelector('#approve-assignment').disabled = true;
  await loadTickets();
  await loadDashboard();
}

async function loadTickets() {
  const response = await fetch('/api/tickets');
  const tickets = await response.json();
  ticketList.innerHTML = tickets.map(ticket => `
    <button class="ticket" data-id="${escapeHtml(ticket.id)}"><strong>${escapeHtml(ticket.id)} · ${escapeHtml(ticket.priority)} · ${escapeHtml(ticket.status || 'New')}</strong><span>${escapeHtml(ticket.summary)}</span></button>`).join('');
  document.querySelectorAll('.ticket').forEach(button => button.addEventListener('click', () => showRecommendation(button.dataset.id)));
}

loadTickets().catch(() => { ticketList.innerHTML = '<p>Could not load the local API. Start the server and refresh.</p>'; });

async function loadDashboard() {
  const dashboard = await (await fetch('/api/dashboard')).json();
  document.querySelector('#open-count').textContent = dashboard.open_ticket_count;
  document.querySelector('#assigned-count').textContent = dashboard.assigned_ticket_count;
  document.querySelector('#risk-count').textContent = dashboard.at_risk_count;
}

loadDashboard();

ticketForm.addEventListener('submit', async event => {
  event.preventDefault();
  formStatus.textContent = 'Creating local ticket…';
  const payload = Object.fromEntries(new FormData(ticketForm));
  try {
    const response = await fetch('/api/tickets', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!response.ok) throw new Error('Ticket could not be created.');
    const data = await response.json();
    formStatus.textContent = `${data.ticket.id} created successfully.`;
    ticketForm.reset();
    await loadTickets();
    await loadDashboard();
    renderRecommendation(data);
  } catch (error) {
    formStatus.textContent = error.message;
  }
});
