<?php
session_start();

$LOCK_FILE = __DIR__ . '/lock.json';
// Hash generated for 5877
$PIN_HASH = password_hash('5877', PASSWORD_DEFAULT);

// Helper function to get client IP
function get_ip() { return $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1'; }

// Helper function to read locks
function get_locks() {
    global $LOCK_FILE;
    if (!file_exists($LOCK_FILE)) return [];
    $data = file_get_contents($LOCK_FILE);
    return json_decode($data, true) ?: [];
}

// Helper function to save locks
function save_locks($locks) {
    global $LOCK_FILE;
    file_put_contents($LOCK_FILE, json_encode($locks));
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    
    $input = json_decode(file_get_contents('php://input'), true);
    $pin = $input['pin'] ?? '';
    $ip = get_ip();
    
    $locks = get_locks();
    $now = time();
    
    // Check if IP is locked
    if (isset($locks[$ip])) {
        $attempts = $locks[$ip]['attempts'];
        $locked_until = $locks[$ip]['locked_until'];
        
        if ($locked_until > $now) {
            $hours_left = ceil(($locked_until - $now) / 3600);
            echo json_encode(['success' => false, 'error' => "Siden er låst. Prøv igjen om ca $hours_left timer."]);
            exit;
        } else if ($locked_until !== 0) {
            // Lock expired, reset
            $locks[$ip] = ['attempts' => 0, 'locked_until' => 0];
        }
    } else {
        $locks[$ip] = ['attempts' => 0, 'locked_until' => 0];
    }
    
    // Verify PIN
    if (password_verify($pin, $PIN_HASH)) {
        // Success
        $_SESSION['auth'] = true;
        unset($locks[$ip]);
        save_locks($locks);
        echo json_encode(['success' => true]);
        exit;
    } else {
        // Fail
        $locks[$ip]['attempts'] += 1;
        if ($locks[$ip]['attempts'] >= 3) {
            $locks[$ip]['locked_until'] = $now + (3 * 3600); // Lock for 3 hours
            save_locks($locks);
            echo json_encode(['success' => false, 'error' => "Feil PIN. 3 feil oppnådd, siden er låst i 3 timer."]);
        } else {
            $left = 3 - $locks[$ip]['attempts'];
            save_locks($locks);
            echo json_encode(['success' => false, 'error' => "Feil PIN. $left forsøk igjen."]);
        }
        exit;
    }
}
?>
