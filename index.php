<?php
session_start();
// Check authentication
$isAuthenticated = isset($_SESSION['auth']) && $_SESSION['auth'] === true;

if (!$isAuthenticated) {
?>
<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sikkerhetskontroll</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #111827; color: white; }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen">
    <div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-sm text-center">
        <h2 class="text-2xl font-bold mb-6">🔒 Angi PIN-kode</h2>
        <input type="password" id="pin" class="w-full text-center text-xl p-3 mb-4 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500" placeholder="****">
        <button onclick="checkPin()" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-4 rounded transition">Lås opp</button>
        <p id="error-msg" class="text-red-400 mt-4 text-sm"></p>
    </div>

    <script>
        async function checkPin() {
            const pin = document.getElementById('pin').value;
            try {
                const res = await fetch('auth.php', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({pin: pin})
                });
                const data = await res.json();
                if (data.success) {
                    window.location.reload();
                } else {
                    document.getElementById('error-msg').innerText = data.error;
                }
            } catch (e) {
                document.getElementById('error-msg').innerText = "Nettverksfeil.";
            }
        }
        document.getElementById('pin').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') checkPin();
        });
    </script>
</body>
</html>
<?php
    exit;
}
?>
<!-- === MAIN APP HTML === -->
<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ Strømforbruk (Webhotell versjon)</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        darkblue: '#111827',
                        lightbg: '#f3f4f6'
                    }
                }
            }
        }
    </script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        body {
            background-color: #f9fafb;
            color: #111827;
        }
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #111827;
                color: #f9fafb;
            }
            .card {
                background-color: #1f2937;
                border-color: #374151;
            }
            .table-head {
                background-color: #374151;
                color: #e5e7eb;
            }
            .table-row {
                border-bottom-color: #374151;
            }
            .table-sum {
                background-color: #262730;
                color: #e5e7eb;
                font-weight: bold;
                border-top: 2px solid #4b5563;
            }
        }
        @media (prefers-color-scheme: light) {
            .card {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            }
            .table-head {
                background-color: #f3f4f6;
                color: #374151;
            }
            .table-row {
                border-bottom: 1px solid #e5e7eb;
            }
            .table-sum {
                background-color: #f9fafb;
                color: #111827;
                font-weight: bold;
                border-top: 2px solid #d1d5db;
            }
        }
        .table-cell {
            padding: 0.75rem 1rem;
            white-space: nowrap;
        }
    </style>
</head>
<body class="p-4 md:p-8 font-sans antialiased">
    <div class="max-w-7xl mx-auto">
        <header class="mb-8 relative">
            <h1 class="text-3xl md:text-5xl font-extrabold tracking-tight mb-2">⚡ Strømforbruk</h1>
            <p class="text-gray-500 dark:text-gray-400">Rask versjon optimalisert for eget webhotell</p>
        </header>

        <div id="loading" class="flex justify-center items-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>

        <div id="app-content" class="hidden space-y-8">
            <!-- Controls -->
            <div class="card p-6 rounded-xl">
                <h2 class="text-lg font-semibold mb-4">Filtrering</h2>
                <div class="flex flex-wrap gap-4" id="device-filters">
                    <!-- Checkboxes injiseres her via JS -->
                </div>
            </div>

            <!-- Table -->
            <div class="card rounded-xl overflow-hidden overflow-x-auto">
                <table class="w-full text-sm text-left">
                    <thead class="table-head">
                        <tr id="table-header-row">
                            <!-- Kolonner injiseres her -->
                        </tr>
                    </thead>
                    <tbody id="table-body">
                        <!-- Rader injiseres her -->
                    </tbody>
                    <tfoot class="table-head">
                        <tr id="table-footer-row">
                            <!-- Footer -->
                        </tr>
                    </tfoot>
                </table>
            </div>

            <!-- Chart -->
            <div class="card p-6 rounded-xl">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl font-bold">📊 Sammenligning av år</h2>
                    <label class="inline-flex items-center space-x-2 text-sm text-gray-400">
                        <input type="checkbox" id="ytd-toggle" class="rounded text-blue-500 focus:ring-blue-500 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600">
                        <span>Hittil i år (YTD)</span>
                    </label>
                </div>
                <div class="w-full h-[500px]">
                    <canvas id="energyChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- Logic -->
    <script src="app.js"></script>
</body>
</html>
