document.addEventListener('DOMContentLoaded', function() {
  const ctx = document.getElementById('orderChart');
  if (ctx && window.orderChartLabels && window.orderChartData) {
    new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: {
        labels: window.orderChartLabels,
        datasets: [{
          label: 'Total Order',
          data: window.orderChartData,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.2)',
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }
});

function cekStatus(refId, rowId) {
  fetch(`/check-order-status/${refId}/`)
    .then(res => res.json())
    .then(data => {
      const statusCell = document.getElementById(`status-${rowId}`);
      if (statusCell) {
        statusCell.innerHTML = `<span class="status-badge status-${data.status}">${data.status}</span>`;
      }
      alert(`Status order #${rowId}: ${data.status}`);
    })
    .catch(err => {
      console.error("Gagal cek status:", err);
      alert("Terjadi kesalahan saat cek status.");
    });
}

