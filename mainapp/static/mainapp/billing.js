// billing.js
async function generateBill() {
    try {
        const email = document.getElementById("customer_email").value;
        const amountPaid = document.getElementById("amount_paid").value;

        const productRows = document.querySelectorAll(".product-row");
        const products = [];

        productRows.forEach(row => {
            const productId = row.querySelector(".product_id").value;
            const quantity = row.querySelector(".quantity").value;
            if (productId && quantity) {
                products.push({
                    product_id: parseInt(productId),
                    quantity: parseInt(quantity)
                });
            }
        });

        const paidDenomination = {
            500: parseInt(document.getElementById("d500")?.value || 0),
            50: parseInt(document.getElementById("d50")?.value || 0),
            20: parseInt(document.getElementById("d20")?.value || 0),
            10: parseInt(document.getElementById("d10")?.value || 0),
            5: parseInt(document.getElementById("d5")?.value || 0),
            2: parseInt(document.getElementById("d2")?.value || 0),
            1: parseInt(document.getElementById("d1")?.value || 0)
        };

        const response = await fetch("/api/generate-bill/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                customer_email: email,
                products: products,
                amount_paid: amountPaid,
                paid_denomination: paidDenomination
            })
        });

        const data = await response.json();

        if (data.status === "success") {
            alert("Bill Generated Successfully!");

            // Fetch the bill details using purchase_id
            const purchaseId = data.purchase_id;
            const billResponse = await fetch(`/bill-details/${purchaseId}/`);
            const billData = await billResponse.json();

            // Display the bill
            displayBill(billData);
        } else {
            alert(data.message);
        }
    } catch (err) {
        alert("Error generating bill. Please try again.");
        console.error(err);
    }
}

function displayBill(billData) {
    const container = document.getElementById("billDetails");
    container.innerHTML = "<h3>Generated Bill</h3>";

    let html = `<p>Purchase ID: ${billData.purchase_id}</p>`;
    html += `<p>Customer Email: ${billData.customer_email}</p>`;
    html += `<table border="1" cellpadding="5">
                <tr><th>Product ID</th><th>Quantity</th><th>Price</th></tr>`;

    billData.products.forEach(p => {
        html += `<tr>
                    <td>${p.product_id}</td>
                    <td>${p.quantity}</td>
                    <td>${p.price}</td>
                 </tr>`;
    });

    html += `</table>`;
    html += `<p>Total Amount: ${billData.total_amount}</p>`;

    container.innerHTML = html;
}