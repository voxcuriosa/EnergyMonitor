<?php
session_start();
if (!isset($_SESSION['auth']) || $_SESSION['auth'] !== true) {
    header('HTTP/1.1 403 Forbidden');
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *'); // For testing purposes

$host = "{{DB_HOST}}";
$user = "{{DB_USER}}";
$pass = "{{DB_PASS}}";
$dbname = "{{DB_NAME}}";

$mysqli = new mysqli($host, $user, $pass, $dbname);

if ($mysqli->connect_error) {
    echo json_encode(['error' => 'Connect Error: ' . $mysqli->connect_error]);
    exit;
}

$query = "SELECT timestamp, device_id, device_name, power_w, energy_kwh FROM energy_readings ORDER BY timestamp ASC";
$result = $mysqli->query($query);

$data = [];
if ($result) {
    while ($row = $result->fetch_assoc()) {
        // Convert to proper types
        $data[] = [
            'timestamp' => $row['timestamp'],
            'device_id' => $row['device_id'],
            'device_name' => $row['device_name'],
            'power_w' => (float)$row['power_w'],
            'energy_kwh' => (float)$row['energy_kwh']
        ];
    }
    $result->free();
} else {
    echo json_encode(['error' => 'Query Error: ' . $mysqli->error]);
    exit;
}

$mysqli->close();

echo json_encode($data);
?>
