
document.addEventListener('DOMContentLoaded', function() {
    const tg = window.Telegram.WebApp;
    tg.ready();

    // --- Hardware Control --- //
    document.getElementById('light-on-btn').addEventListener('click', () => {
        // Sending data to the bot
        tg.sendData(JSON.stringify({ type: 'hardware_control', device: 'light', command: 'ON' }));
    });

    document.getElementById('light-off-btn').addEventListener('click', () => {
        tg.sendData(JSON.stringify({ type: 'hardware_control', device: 'light', command: 'OFF' }));
    });

    document.getElementById('ac-on-btn').addEventListener('click', () => {
        tg.sendData(JSON.stringify({ type: 'hardware_control', device: 'ac', command: 'ON' }));
    });

    document.getElementById('ac-off-btn').addEventListener('click', () => {
        tg.sendData(JSON.stringify({ type: 'hardware_control', device: 'ac', command: 'OFF' }));
    });

    // --- Expense Form --- //
    const expenseForm = document.getElementById('expense-form');
    expenseForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const description = document.getElementById('expense-desc').value;
        const amount = document.getElementById('expense-amount').value;
        const category = document.getElementById('expense-category').value;

        if (description && amount) {
            const expenseData = {
                type: 'expense_add',
                description: description,
                amount: parseFloat(amount),
                category: category
            };
            // Send the data to the bot
            tg.sendData(JSON.stringify(expenseData));
            
            // Optional: Show feedback to user and close web app
            tg.showPopup({title: "Success", message: "Expense has been recorded."}, () => {
                tg.close();
            });

        } else {
            tg.showAlert('Please fill in all fields.');
        }
    });

});
