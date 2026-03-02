// billing.js

// Generate Bill
async function generateBill() {
    try {
        const email = document.getElementById("customer_email").value;
        const amountPaid = parseFloat(document.getElementById("amount_paid").value);

        // Validate email
        if (!email) {
            alert("Enter customer email");
            return;
        }

        // Validate amount paid
        if (isNaN(amountPaid) || amountPaid <= 0) {
            alert("Enter a valid amount paid");
            return;
        }

        // Collect products from product rows
        const productRows = document.querySelectorAll(".product-row");
        const products = [];

        productRows.forEach(row => {
            const pid = parseInt(row.querySelector(".product_id")?.value);
            const qty = parseInt(row.querySelector(".quantity")?.value);
            if (!isNaN(pid) && !isNaN(qty) && qty > 0) {
                products.push({ product_id: pid, quantity: qty });
            }
        });

        if (products.length === 0) {
            alert("Add at least one valid product");
            return;
        }

        // Collect denomination values
        const paidDenomination = {
            500: parseInt(document.getElementById("d500")?.value || 0),
            50:  parseInt(document.getElementById("d50")?.value  || 0),
            20:  parseInt(document.getElementById("d20")?.value  || 0),
            10:  parseInt(document.getElementById("d10")?.value  || 0),
            5:   parseInt(document.getElementById("d5")?.value   || 0),
            2:   parseInt(document.getElementById("d2")?.value   || 0),
            1:   parseInt(document.getElementById("d1")?.value   || 0)
        };

        // Call backend to generate bill
        const response = await fetch("/api/generate-bill/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                customer_email: email,
                products,
                amount_paid: amountPaid,
                paid_denomination: paidDenomination
            })
        });

        if (!response.ok) {
            alert(`Server error: ${response.status} ${response.statusText}`);
            return;
        }

        const data = await response.json();

        if (data.status !== "success") {
            alert("Error generating bill: " + (data.message || "Unknown error"));
            return;
        }

        if (!data.purchase_id) {
            alert("Bill generated but no purchase ID returned.");
            return;
        }

        // Fetch full bill details using purchase ID
        const billResp = await fetch(`/api/bill-details/${data.purchase_id}/`);

        if (!billResp.ok) {
            alert(`Failed to fetch bill details: ${billResp.status} ${billResp.statusText}`);
            return;
        }

        const billData = await billResp.json();

        console.log("Full bill response:", JSON.stringify(billData, null, 2));

        if (billData.status === "success" && billData.data) {
            displayBill(billData.data);
        } else if (billData.status === "success" && !billData.data) {
            console.warn("Bill details data is missing:", billData);
            alert("Bill generated, but no details found.");
        } else {
            alert("Failed to fetch bill details: " + (billData.message || "Unknown error"));
        }

    } catch (err) {
        console.error("Unexpected error in generateBill:", err);
        alert("Unexpected error occurred. Check console.");
    }
}
// View purchase history
async function view() {
    const email = document.getElementById("customer_email").value;

    if (!email) {
        alert("Enter customer email to view history");
        return;
    }

    try {
        const response = await fetch(`/api/purchase-history/?email=${encodeURIComponent(email)}`);
        if (!response.ok) throw new Error(`Error fetching history: ${response.statusText}`);

        const result = await response.json();

        if (result.status !== "success" || !Array.isArray(result.data) || result.data.length === 0) {
            alert("No purchase history found for this email.");
            return;
        }

        renderPurchaseHistory(result.data);

    } catch (err) {
        console.error(err);
        alert("Failed to fetch purchase history. Check console for details.");
    }
}

// Render purchase history table
function renderPurchaseHistory(purchases) {
    const container = document.getElementById("billDetails");
    let html = `<h3>Purchase History</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="width:100%; border-collapse: collapse;">
            <tr>
                <th>Purchase ID</th>
                <th>Date</th>
                <th>Net Total</th>
            </tr>`;

    purchases.forEach(p => {
        const date = p.date ? new Date(p.date).toLocaleString() : "-";
        const netTotal = (p.net_total ?? 0).toFixed(2);

        html += `
            <tr>
                <td>${p.purchase_id}</td>
                <td>${date}</td>
                <td>₹${netTotal}</td>
            </tr>`;
    });

    html += `</table>`;
    container.innerHTML = html;
}

function displayBill(bill) {
    if (!bill) return;

    const container = document.getElementById("billModalContent");
    container.innerHTML = "<h3>Generated Bill</h3>";

    // Customer info
    let html = `<p>Purchase ID: ${bill.purchase_id || "N/A"}</p>`;
    html += `<p>Customer Email: ${bill.customer_email || "N/A"}</p>`;

    // Products table
    const items = bill.items || [];
    if (items.length > 0) {
        html += `<table border="1" cellpadding="5" style="width:100%; border-collapse: collapse;">
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Unit Price</th>
                <th>Qty</th>
                <th>Purchase Price</th>
                <th>Tax %</th>
                <th>Tax Payable</th>
                <th>Total Price</th>
            </tr>`;
        items.forEach(item => {
            html += `<tr>
                <td>${item.product_id || "-"}</td>
                <td>${item.product_name || "-"}</td>
                <td>${parseFloat(item.unit_price || 0).toFixed(2)}</td>
                <td>${item.quantity || 0}</td>
                <td>${parseFloat(item.purchase_price || 0).toFixed(2)}</td>
                <td>${parseFloat(item.tax_percentage || 0).toFixed(2)}</td>
                <td>${parseFloat(item.tax_amount || 0).toFixed(2)}</td>
                <td>${parseFloat(item.total_price || 0).toFixed(2)}</td>
            </tr>`;
        });
        html += `</table>`;
    } else {
        html += "<p>No items purchased.</p>";
    }

    
    const s = bill.summary || {};
    html += `<h4>Summary</h4>`;
    html += `<p>Total without tax: ${parseFloat(s.total_without_tax || 0).toFixed(2)}</p>`;
    html += `<p>Total tax: ${parseFloat(s.total_tax || 0).toFixed(2)}</p>`;
    html += `<p>Net total: ${parseFloat(s.net_total || 0).toFixed(2)}</p>`;
    html += `<p>Rounded total: ${parseFloat(s.rounded_total || 0).toFixed(2)}</p>`;
    html += `<p>Amount Paid: ${parseFloat(s.amount_paid || 0).toFixed(2)}</p>`;
    html += `<p>Balance: ${parseFloat(s.balance || 0).toFixed(2)}</p>`;

   
    const change = bill.change_given || {};
    const changeKeys = Object.keys(change);
    if (changeKeys.length > 0) {
        html += `<h4>Change Given</h4><ul>`;
        changeKeys.forEach(denom => {
            html += `<li>${denom} x ${change[denom]}</li>`;
        });
        html += `</ul>`;
    }

    container.innerHTML = html;

    document.getElementById("billModal").style.display = "block";
}


function closeBillModal() {
    document.getElementById("billModal").style.display = "none";
}
