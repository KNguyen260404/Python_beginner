// Main JavaScript for Web Server UI

// Auto-refresh stats on admin page
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the admin page
    const cpuChart = document.getElementById('cpuChart');
    if (cpuChart) {
        // Set up auto-refresh for stats
        setInterval(refreshStats, 10000); // Refresh every 10 seconds
    }
});

// Function to refresh server stats
function refreshStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            // Update CPU chart
            updateChart('cpuChart', [data.cpu_percent, 100 - data.cpu_percent]);
            
            // Update Memory chart
            updateChart('memoryChart', [data.memory_percent, 100 - data.memory_percent]);
            
            // Update Disk chart
            updateChart('diskChart', [data.disk_percent, 100 - data.disk_percent]);
            
            // Update text displays
            document.querySelector('h5:contains("CPU")').textContent = `CPU: ${data.cpu_percent}%`;
            document.querySelector('h5:contains("RAM")').textContent = `RAM: ${data.memory_percent}%`;
            document.querySelector('h5:contains("Disk")').textContent = `Disk: ${data.disk_percent}%`;
            
            // Format bandwidth
            let bandwidth = data.bandwidth_usage;
            let bandwidthStr = '';
            
            if (bandwidth < 1024) {
                bandwidthStr = `${bandwidth} B`;
            } else if (bandwidth < 1024 * 1024) {
                bandwidthStr = `${(bandwidth / 1024).toFixed(2)} KB`;
            } else {
                bandwidthStr = `${(bandwidth / (1024 * 1024)).toFixed(2)} MB`;
            }
            
            // Update stats cards
            const statsCards = document.querySelectorAll('.stats-card h3');
            if (statsCards.length >= 3) {
                // Format uptime
                const uptime = data.uptime;
                const days = Math.floor(uptime / 86400);
                const hours = Math.floor((uptime % 86400) / 3600);
                const minutes = Math.floor((uptime % 3600) / 60);
                const seconds = Math.floor(uptime % 60);
                const uptimeStr = `${days}d ${hours}h ${minutes}m ${seconds}s`;
                
                statsCards[0].textContent = uptimeStr;
                statsCards[1].textContent = data.requests;
                statsCards[2].textContent = bandwidthStr;
                statsCards[3].textContent = data.errors;
            }
        })
        .catch(error => console.error('Error fetching stats:', error));
}

// Function to update chart data
function updateChart(chartId, newData) {
    const chart = Chart.getChart(chartId);
    if (chart) {
        chart.data.datasets[0].data = newData;
        chart.update();
    }
}

// Fix for querySelector with contains
// This is needed because the standard querySelector doesn't support :contains
if (!document.querySelector('h5:contains("CPU")')) {
    // Polyfill for :contains selector
    jQuery.expr[':'].contains = function(a, i, m) {
        return jQuery(a).text().toUpperCase()
            .indexOf(m[3].toUpperCase()) >= 0;
    };
}

// File upload validation
const fileUpload = document.querySelector('input[type="file"]');
if (fileUpload) {
    fileUpload.addEventListener('change', function() {
        const fileName = this.value.split('\\').pop();
        if (fileName) {
            // Check if file extension is allowed
            const fileExt = fileName.split('.').pop().toLowerCase();
            const allowedExts = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'html', 'css', 'js'];
            
            if (!allowedExts.includes(fileExt)) {
                alert('Định dạng file không được hỗ trợ!');
                this.value = '';
            }
        }
    });
}

// Add fade-in animation to cards
const cards = document.querySelectorAll('.card');
cards.forEach(card => {
    card.classList.add('fade-in');
});