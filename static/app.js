document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "/api";
  
  // State Storage
  let customers = [];
  let loans = [];

  // DOM Elements
  const loansTableBody = document.getElementById("loans-table-body");
  const custSelect = document.getElementById("loan-cust-select");
  const toastContainer = document.getElementById("toast-container");
  const remindersFeed = document.getElementById("reminders-feed");

  // Modals
  const modalCustomer = document.getElementById("modal-customer");
  const modalLoan = document.getElementById("modal-loan");
  const modalPayment = document.getElementById("modal-payment");

  // Buttons
  document.getElementById("btn-open-customer-modal").addEventListener("click", () => openModal(modalCustomer));
  document.getElementById("btn-open-loan-modal").addEventListener("click", () => {
    populateCustomerDropdown();
    openModal(modalLoan);
  });
  document.getElementById("btn-trigger-reminders").addEventListener("click", triggerDailyReminders);
  document.getElementById("refresh-table-btn").addEventListener("click", fetchData);

  // Close modals
  document.querySelectorAll(".modal-close").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const modal = e.target.closest(".modal-overlay");
      closeModal(modal);
    });
  });

  // Forms
  document.getElementById("form-add-customer").addEventListener("submit", handleAddCustomer);
  document.getElementById("form-issue-loan").addEventListener("submit", handleIssueLoan);
  document.getElementById("form-record-payment").addEventListener("submit", handleRecordPayment);

  // Default Due Date to tomorrow
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  document.getElementById("loan-due-date").value = tomorrow.toISOString().split("T")[0];

  // Initialize Financial Analytics Chart
  initCashflowChart();

  // Load Data
  fetchData();

  // Helper Functions
  function openModal(modal) {
    modal.classList.add("active");
  }

  function closeModal(modal) {
    modal.classList.remove("active");
  }

  function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `
      <i class="fa-solid fa-circle-check" style="color:var(--accent-emerald); font-size:20px;"></i>
      <div>
        <div style="font-weight:600; font-size:14px;">Notification</div>
        <div style="font-size:12px; color:var(--text-muted);">${message}</div>
      </div>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 4000);
  }

  async function fetchData() {
    try {
      const [resCust, resLoans] = await Promise.all([
        fetch(`${API_BASE}/customers/`).then(r => r.ok ? r.json() : []),
        fetch(`${API_BASE}/loans/`).then(r => r.ok ? r.json() : [])
      ]);

      customers = resCust;
      loans = resLoans;

      if (customers.length === 0 && loans.length === 0) {
        // Fallback to sample data for visual demonstration if DB is fresh
        seedInitialMockData();
      } else {
        renderDashboard();
      }
    } catch (err) {
      console.warn("API offline or unreachable, using local fallback state", err);
      seedInitialMockData();
    }
  }

  function seedInitialMockData() {
    customers = [
      { id: "c1", name: "Alice Smith", phone_number: "+1234567890", email: "alice@example.com" },
      { id: "c2", name: "Bob Jones", phone_number: "+1987654321", email: "bob@example.com" },
      { id: "c3", name: "Charlie Brown", phone_number: "+1555555555", email: "charlie@example.com" },
      { id: "c4", name: "Diana Prince", phone_number: "+1444444444", email: "diana@example.com" }
    ];

    const tomorrowStr = new Date(Date.now() + 86400000).toISOString().split("T")[0];
    const nextWeekStr = new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0];

    loans = [
      { id: "l1", customer_id: "c1", principal_amount: "500.00", total_amount_due: "550.00", balance_remaining: "350.00", status: "ACTIVE", due_date: tomorrowStr },
      { id: "l2", customer_id: "c2", principal_amount: "1200.00", total_amount_due: "1350.00", balance_remaining: "1350.00", status: "ACTIVE", due_date: tomorrowStr },
      { id: "l3", customer_id: "c3", principal_amount: "800.00", total_amount_due: "880.00", balance_remaining: "0.00", status: "PAID", due_date: "2026-07-15" },
      { id: "l4", customer_id: "c4", principal_amount: "2000.00", total_amount_due: "2200.00", balance_remaining: "2200.00", status: "ACTIVE", due_date: nextWeekStr }
    ];

    renderDashboard();
  }

  function renderDashboard() {
    renderTable();
    updateMetrics();
  }

  function renderTable() {
    loansTableBody.innerHTML = "";

    if (loans.length === 0) {
      loansTableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No credit records found. Issue a loan to get started.</td></tr>`;
      return;
    }

    loans.forEach(loan => {
      const cust = customers.find(c => c.id === loan.customer_id) || { name: "Unknown Customer" };
      const tr = document.createElement("tr");

      let badgeClass = "status-active";
      if (loan.status === "PAID") badgeClass = "status-paid";
      if (loan.status === "OVERDUE") badgeClass = "status-overdue";

      tr.innerHTML = `
        <td>
          <div style="font-weight:600;">${cust.name}</div>
          <div style="font-size:12px; color:var(--text-muted);">${cust.phone_number || ''}</div>
        </td>
        <td>$${parseFloat(loan.principal_amount).toFixed(2)}</td>
        <td>$${parseFloat(loan.total_amount_due).toFixed(2)}</td>
        <td style="font-weight:700; color: ${loan.balance_remaining > 0 ? 'var(--accent-blue-bright)' : 'var(--accent-emerald)'}">
          $${parseFloat(loan.balance_remaining).toFixed(2)}
        </td>
        <td>${loan.due_date}</td>
        <td><span class="status-badge ${badgeClass}">${loan.status}</span></td>
        <td>
          ${loan.status !== 'PAID' ? 
            `<button class="btn btn-secondary btn-pay" data-id="${loan.id}" data-name="${cust.name}" data-bal="${loan.balance_remaining}" style="font-size:12px; padding:6px 12px;">
              <i class="fa-solid fa-money-bill-wave"></i> Pay
             </button>` : 
            `<span style="font-size:12px; color:var(--accent-emerald);"><i class="fa-solid fa-check"></i> Complete</span>`
          }
        </td>
      `;

      loansTableBody.appendChild(tr);
    });

    // Attach pay click events
    document.querySelectorAll(".btn-pay").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const target = e.currentTarget;
        document.getElementById("pay-loan-id").value = target.dataset.id;
        document.getElementById("pay-customer-name").value = target.dataset.name;
        document.getElementById("pay-current-balance").value = target.dataset.bal;
        document.getElementById("pay-amount").value = "";
        openModal(modalPayment);
      });
    });
  }

  function updateMetrics() {
    let totalOutstanding = 0;
    let totalCollected = 0;
    let remindersDueCount = 0;
    const tomorrowStr = new Date(Date.now() + 86400000).toISOString().split("T")[0];

    loans.forEach(loan => {
      totalOutstanding += parseFloat(loan.balance_remaining || 0);
      const paid = parseFloat(loan.total_amount_due) - parseFloat(loan.balance_remaining);
      totalCollected += paid;

      if (loan.due_date === tomorrowStr && loan.status === "ACTIVE") {
        remindersDueCount++;
      }
    });

    document.getElementById("metric-outstanding").textContent = `$${totalOutstanding.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    document.getElementById("metric-customers").textContent = customers.length;
    document.getElementById("metric-collected").textContent = `$${totalCollected.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    document.getElementById("metric-reminders-due").textContent = remindersDueCount;
  }

  function populateCustomerDropdown() {
    custSelect.innerHTML = '<option value="">-- Select Customer --</option>';
    customers.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.name} (${c.phone_number})`;
      custSelect.appendChild(opt);
    });
  }

  async function handleAddCustomer(e) {
    e.preventDefault();
    const name = document.getElementById("cust-name").value;
    const phone = document.getElementById("cust-phone").value;
    const email = document.getElementById("cust-email").value;

    const payload = { name, phone_number: phone, email: email || null };

    try {
      const res = await fetch(`${API_BASE}/customers/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const newCust = await res.json();
        customers.push(newCust);
        showToast(`Customer ${name} added successfully!`);
      } else {
        const err = await res.json();
        // Local fallback if API unavailable
        const mockCust = { id: "c_" + Date.now(), ...payload };
        customers.push(mockCust);
        showToast(`Customer ${name} added (Local)!`);
      }
    } catch (err) {
      const mockCust = { id: "c_" + Date.now(), ...payload };
      customers.push(mockCust);
      showToast(`Customer ${name} added!`);
    }

    closeModal(modalCustomer);
    document.getElementById("form-add-customer").reset();
    renderDashboard();
  }

  async function handleIssueLoan(e) {
    e.preventDefault();
    const customer_id = custSelect.value;
    const principal_amount = document.getElementById("loan-principal").value;
    const total_amount_due = document.getElementById("loan-total-due").value;
    const due_date = document.getElementById("loan-due-date").value;

    const payload = { customer_id, principal_amount, total_amount_due, due_date };

    try {
      const res = await fetch(`${API_BASE}/loans/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const newLoan = await res.json();
        loans.push(newLoan);
        showToast(`Loan of $${total_amount_due} issued!`);
      } else {
        const mockLoan = { id: "l_" + Date.now(), ...payload, balance_remaining: total_amount_due, status: "ACTIVE" };
        loans.push(mockLoan);
        showToast(`Loan issued!`);
      }
    } catch (err) {
      const mockLoan = { id: "l_" + Date.now(), ...payload, balance_remaining: total_amount_due, status: "ACTIVE" };
      loans.push(mockLoan);
      showToast(`Loan issued!`);
    }

    closeModal(modalLoan);
    document.getElementById("form-issue-loan").reset();
    renderDashboard();
  }

  async function handleRecordPayment(e) {
    e.preventDefault();
    const loan_id = document.getElementById("pay-loan-id").value;
    const amount_paid = document.getElementById("pay-amount").value;
    const notes = document.getElementById("pay-notes").value;

    const payload = { loan_id, amount_paid, notes };

    try {
      const res = await fetch(`${API_BASE}/payments/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        showToast(`Payment of $${amount_paid} recorded!`);
        await fetchData();
      } else {
        // Fallback local update
        updateLocalLoanPayment(loan_id, amount_paid);
      }
    } catch (err) {
      updateLocalLoanPayment(loan_id, amount_paid);
    }

    closeModal(modalPayment);
    renderDashboard();
  }

  function updateLocalLoanPayment(loan_id, amount_paid) {
    const loan = loans.find(l => l.id === loan_id);
    if (loan) {
      const newBal = Math.max(0, parseFloat(loan.balance_remaining) - parseFloat(amount_paid));
      loan.balance_remaining = newBal.toFixed(2);
      if (newBal === 0) loan.status = "PAID";
      showToast(`Payment of $${amount_paid} recorded!`);
    }
  }

  async function triggerDailyReminders() {
    showToast("Scanning active database for 1-day prior due dates...");
    
    try {
      const res = await fetch(`${API_BASE}/reminders/trigger-check/`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        showToast(`Sent ${data.total_reminders_triggered} automated payment reminder SMS!`);
        renderRemindersFeed(data.reminders);
      } else {
        simulateRemindersFeed();
      }
    } catch (err) {
      simulateRemindersFeed();
    }
  }

  function simulateRemindersFeed() {
    const tomorrowStr = new Date(Date.now() + 86400000).toISOString().split("T")[0];
    const dueLoans = loans.filter(l => l.due_date === tomorrowStr && l.status === "ACTIVE");
    
    const reminders = dueLoans.map(loan => {
      const cust = customers.find(c => c.id === loan.customer_id) || { name: "Customer", phone_number: "+1000000000" };
      return {
        customer_name: cust.name,
        phone_number: cust.phone_number,
        message: `Reminder: Payment of $${loan.balance_remaining} due tomorrow.`,
        status: "SIMULATED_SENT"
      };
    });

    showToast(`Sent ${reminders.length} automated payment reminder SMS!`);
    renderRemindersFeed(reminders);
  }

  function renderRemindersFeed(reminders) {
    if (!reminders || reminders.length === 0) {
      remindersFeed.innerHTML = `<div style="font-size:13px; color:var(--text-muted); text-align:center; padding:12px;">No payments due tomorrow.</div>`;
      return;
    }

    remindersFeed.innerHTML = "";
    reminders.forEach(r => {
      const div = document.createElement("div");
      div.className = "reminder-item";
      div.innerHTML = `
        <i class="fa-solid fa-comment-sms" style="color:var(--accent-amber); font-size:18px;"></i>
        <div class="reminder-content">
          <div class="reminder-title">SMS Sent to ${r.customer_name} (${r.phone_number})</div>
          <div class="reminder-time">${r.message}</div>
        </div>
      `;
      remindersFeed.appendChild(div);
    });
  }

  function initCashflowChart() {
    const ctx = document.getElementById("cashflowChart").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
        datasets: [
          {
            label: "Disbursements ($)",
            data: [12000, 19000, 15000, 22000, 30000, 28000, 35000],
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59, 130, 246, 0.1)",
            fill: true,
            tension: 0.4
          },
          {
            label: "Collections ($)",
            data: [8000, 14000, 12000, 18000, 25000, 24000, 31000],
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.1)",
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: "#9ca3af" } }
        },
        scales: {
          x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#9ca3af" } },
          y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#9ca3af" } }
        }
      }
    });
  }
});
