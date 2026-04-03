document.addEventListener('DOMContentLoaded', async () => {
    
    // --- Data structures ---
    const manual_data = {
        2024: {
            1: {"Totalt": 3386, "Easee": 544}, 
            2: {"Totalt": 2466, "Easee": 403}, 
            3: {"Totalt": 1826, "Easee": 236}, 
            4: {"Totalt": 2036, "Easee": 247}, 
            5: {"Totalt": 1405, "Easee": 343}, 
            6: {"Totalt": 1495, "Easee": 386},
            7: {"Totalt": 1313, "Easee": 287}, 
            8: {"Totalt": 1456, "Easee": 384}, 
            9: {"Totalt": 1511, "Easee": 394}, 
            10: {"Totalt": 1802, "Easee": 341}, 
            11: {"Totalt": 2273, "Easee": 396}, 
            12: {"Totalt": 2833, "Easee": 523}
        },
        2025: {
            1: {"Totalt": 3148, "Easee": 593}, 
            2: {"Totalt": 2654, "Easee": 445}, 
            3: {"Totalt": 2362, "Easee": 332}, 
            4: {"Totalt": 1679, "Easee": 190}, 
            5: {"Totalt": 1549, "Easee": 282}, 
            6: {"Totalt": 1099, "Easee": 225},
            7: {"Totalt": 1199, "Easee": 289}, 
            8: {"Totalt": 1224, "Easee": 265}, 
            9: {"Totalt": 1382, "Easee": 262}, 
            10: {"Totalt": 1921, "Easee": 454}, 
            11: {"Totalt": 2172, "Easee": 456}, 
            12: {"Totalt": 2561, "Easee": 514}
        },
        2026: {
            3: {
                "Varmepumpe": 500, // Fikser Mars 2026 fordi varmepumpen frøs
                "Fryser": 10.52    // Fra 1052.0 delt på 100 grunnet kommafeil i måler
            }
        }
    };

    const estimates_2025 = {
        3: 62, 4: 243, 5: 97, 6: 180, 7: 146, 8: 142, 9: 165, 10: 310, 11: 392
    };

    const month_names = ["Januar", "Februar", "Mars", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Desember"];
    const ignored_devices = ['Vann', 'Tibber puls'];
    const default_hidden = ["Kjellerstue - Varmeovn", "Kjellerstue - Varmekabler ", "Vaskerom - varme", "Smartplugg", "Smartplugg "];
    let rawData = [];
    let devices = [];
    let tableRows = [];
    let visibleDevices = [];
    let chartInstance = null;

    // --- Fetch Data ---
    try {
        const response = await fetch('api.php');
        if (!response.ok) throw new Error('Nettverksfeil ved henting av api.php');
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        rawData = data.map(d => ({
            ...d,
            timestamp: new Date(d.timestamp)
        })).filter(d => !ignored_devices.includes(d.device_name));

    } catch (e) {
        document.getElementById('loading').innerHTML = `
            <div class="text-red-500 font-bold p-4 bg-red-100 rounded-lg">
                Fikk ikke hentet data: ${e.message}<br>
                <em>Er API-et riktig konfigurert med database-tilgang?</em>
            </div>
        `;
        return;
    }

    // Hide loading
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('app-content').classList.remove('hidden');

    // Get unique sorted devices
    devices = [...new Set(rawData.map(d => d.device_name))].sort();
    
    // Fallback: If Totalt missing but in manual data, ensure it's in list
    if (!devices.includes("Totalt")) devices.unshift("Totalt");

    // Init visible devices
    visibleDevices = devices.filter(d => !default_hidden.includes(d));

    // --- Create Filter UI ---
    const filterContainer = document.getElementById('device-filters');
    devices.forEach(dev => {
        const lbl = document.createElement('label');
        lbl.className = 'inline-flex items-center space-x-2 cursor-pointer bg-white dark:bg-gray-800 px-3 py-1.5 rounded-full border border-gray-300 dark:border-gray-600 shadow-sm text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition';
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.value = dev;
        cb.checked = visibleDevices.includes(dev);
        cb.className = 'rounded text-blue-500 focus:ring-blue-500 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600';
        
        cb.addEventListener('change', (e) => {
            if (e.target.checked) visibleDevices.push(dev);
            else visibleDevices = visibleDevices.filter(d => d !== dev);
            renderTable();
            renderChart();
        });

        lbl.appendChild(cb);
        lbl.appendChild(document.createTextNode(dev));
        filterContainer.appendChild(lbl);
    });

    // --- Data Processing (The Pandas Equivalent) ---
    function getReading(date, deviceName) {
        const devData = rawData.filter(d => d.device_name === deviceName);
        if (devData.length === 0) return null;

        // Exact or near match within 6 days forward
        const windowEnd = new Date(date);
        windowEnd.setDate(windowEnd.getDate() + 6);

        const matches = devData.filter(d => d.timestamp >= date && d.timestamp <= windowEnd);
        if (matches.length > 0) {
            // sort ascending
            matches.sort((a,b) => a.timestamp - b.timestamp);
            return matches[0].energy_kwh;
        }
        return null;
    }

    function processData() {
        tableRows = [];
        const currentYear = new Date().getFullYear();
        const startYear = 2023;
        
        for (let year = startYear; year <= currentYear; year++) {
            let hasDataForYear = false;
            let yearTotals = {};
            devices.forEach(d => yearTotals[d] = 0);

            for (let month = 1; month <= 12; month++) {
                const startDate = new Date(year, month - 1, 1);
                const endDate = month === 12 ? new Date(year + 1, 0, 1) : new Date(year, month, 1);
                
                let rowData = { "Periode": `${month_names[month-1]} ${year}` };
                let hasMonthData = false;

                devices.forEach(dev => {
                    // Estimate inject
                    if (year === 2025 && month in estimates_2025 && dev === "Bad kjeller - Varmekabler") {
                        const cons = estimates_2025[month];
                        rowData[dev] = `${cons} (Est)`;
                        yearTotals[dev] += cons;
                        hasMonthData = true;
                        return;
                    }

                    const valStart = getReading(startDate, dev);
                    const valEnd = getReading(endDate, dev);

                    let consumption = "";
                    if (valStart !== null && valEnd !== null) {
                        let diff = valEnd - valStart;
                        if (diff < 0) diff = valEnd; // Reset logic fallback
                        
                        consumption = Math.round(diff);
                        rowData[dev] = consumption;
                        yearTotals[dev] += diff;
                        hasMonthData = true;
                    } else {
                        rowData[dev] = "";
                    }
                });

                // Manual Data inject
                if (manual_data[year] && manual_data[year][month]) {
                    hasMonthData = true;
                    Object.keys(manual_data[year][month]).forEach(dev => {
                        rowData[dev] = manual_data[year][month][dev];
                    });
                }

                if (hasMonthData) {
                    tableRows.push(rowData);
                    hasDataForYear = true;
                }
            }

            // Sum Row
            if (hasDataForYear) {
                let sumRow = { "Periode": `SUM ${year}`, isSum: true };
                
                devices.forEach(dev => {
                    // Try to calculate absolute sum from year start to end
                    const startDate = new Date(year, 0, 1);
                    const endDate = new Date(year + 1, 0, 1);
                    
                    const devReadings = rawData.filter(d => d.device_name === dev && d.timestamp >= startDate && d.timestamp <= endDate)
                                               .sort((a,b) => a.timestamp - b.timestamp);
                    
                    let totalAcc = 0;
                    if (devReadings.length > 0) {
                        let prevVal = devReadings[0].energy_kwh;
                        for (let i = 1; i < devReadings.length; i++) {
                            let currVal = devReadings[i].energy_kwh;
                            let diff = currVal - prevVal;
                            if (diff < 0) {
                                if (currVal < prevVal * 0.5) totalAcc += currVal;
                                else totalAcc += diff;
                            } else {
                                if (diff < 10000) totalAcc += diff;
                            }
                            prevVal = currVal;
                        }
                    }

                    if (year === 2025 && dev === "Bad kjeller - Varmekabler") {
                        totalAcc = yearTotals[dev];
                    }

                    // Check manual data sums
                    if (manual_data[year]) {
                        let manTotal = 0;
                        let manFound = false;
                        Object.keys(manual_data[year]).forEach(m => {
                            if (manual_data[year][m][dev] !== undefined) {
                                manTotal += manual_data[year][m][dev];
                                manFound = true;
                            }
                        });
                        if (manFound && (!totalAcc || totalAcc < manTotal)) {
                            totalAcc = manTotal;
                        }
                    }

                    sumRow[dev] = totalAcc > 0 ? Math.round(totalAcc) : "0";
                });
                tableRows.push(sumRow);
            }
        }
    }

    // --- Render Table ---
    function renderTable() {
        const thead = document.getElementById('table-header-row');
        const tbody = document.getElementById('table-body');
        const tfoot = document.getElementById('table-footer-row');
        
        thead.innerHTML = '<th class="table-cell">Periode</th>';
        tfoot.innerHTML = '<th class="table-cell text-left">Periode</th>';
        
        // Reorder: Totalt first
        let cols = ["Totalt", ...visibleDevices.filter(d => d !== "Totalt")];

        cols.forEach(dev => {
            const hTh = document.createElement('th');
            hTh.className = 'table-cell';
            hTh.innerText = dev;
            thead.appendChild(hTh);

            const fTh = document.createElement('th');
            fTh.className = 'table-cell text-left';
            fTh.innerText = dev;
            tfoot.appendChild(fTh);
        });

        tbody.innerHTML = '';

        tableRows.forEach(row => {
            const tr = document.createElement('tr');
            tr.className = row.isSum ? 'table-sum' : 'table-row hover:bg-gray-50 dark:hover:bg-gray-700/50 transition';
            
            const pTd = document.createElement('td');
            pTd.className = 'table-cell font-medium';
            pTd.innerHTML = row.isSum ? `<strong>${row.Periode}</strong>` : row.Periode;
            tr.appendChild(pTd);

            cols.forEach(dev => {
                const td = document.createElement('td');
                td.className = 'table-cell';
                let val = row[dev];
                if (val === undefined || val === null || val === "") val = "";
                td.innerHTML = row.isSum ? `<strong>${val}</strong>` : val;
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });
    }

    // --- Render Chart ---
    function renderChart() {
        if (chartInstance) chartInstance.destroy();

        const ctx = document.getElementById('energyChart').getContext('2d');
        const isYTD = document.getElementById('ytd-toggle').checked;
        
        let datasets = [];
        let cols = ["Totalt", ...visibleDevices.filter(d => d !== "Totalt")];
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];
        let labels = cols;

        if (!isYTD) {
            let sumRows = tableRows.filter(r => r.isSum);
            sumRows.forEach((row, idx) => {
                let year = row.Periode.replace("SUM ", "");
                let data = cols.map(dev => {
                    let val = row[dev];
                    if (typeof val === 'string') val = val.replace('<strong>', '').replace('</strong>', '');
                    return parseFloat(val) || 0;
                });

                datasets.push({
                    label: year,
                    data: data,
                    backgroundColor: colors[idx % colors.length],
                    borderRadius: 4
                });
            });
        } else {
            // YTD Logic
            const currentYear = new Date().getFullYear();
            const currentYearMonths = tableRows.filter(r => !r.isSum && r.Periode.includes(currentYear.toString()));
            let maxMonthIdx = 11;
            if (currentYearMonths.length > 0) {
                const lastMonthName = currentYearMonths[currentYearMonths.length-1].Periode.split(" ")[0];
                maxMonthIdx = month_names.indexOf(lastMonthName);
            }

            // Get all years
            let sumRows = tableRows.filter(r => r.isSum);
            sumRows.forEach((row, idx) => {
                let year = row.Periode.replace("SUM ", "").substring(0, 4);
                let ytdData = cols.map(dev => {
                    let acc = 0;
                    // Sum all months for this year up to maxMonthIdx
                    let yearMonths = tableRows.filter(r => !r.isSum && r.Periode.includes(year) && month_names.indexOf(r.Periode.split(" ")[0]) <= maxMonthIdx);
                    yearMonths.forEach(mRow => {
                        let val = mRow[dev];
                        if (typeof val === 'string') val = val.replace(' (Est)', '');
                        acc += parseFloat(val) || 0;
                    });
                    return Math.round(acc);
                });

                datasets.push({
                    label: `${year} (YTD)`,
                    data: ytdData,
                    backgroundColor: colors[idx % colors.length],
                    borderRadius: 4
                });
            });
        }

        Chart.defaults.color = window.matchMedia('(prefers-color-scheme: dark)').matches ? '#9ca3af' : '#4b5563';

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'kWh' },
                        grid: { color: 'rgba(156, 163, 175, 0.1)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }

    document.getElementById('ytd-toggle').addEventListener('change', renderChart);

    // Execute
    processData();
    renderTable();
    renderChart();
});
