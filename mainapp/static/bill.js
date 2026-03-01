window.onload = function () {

    let params = new URLSearchParams(window.location.search);
    let purchase_id = params.get("purchase_id");

    fetch(`/purchase-details/${purchase_id}/`)
        .then(res => res.json())
        .then(data => {

            let html = `
                <p>Email: ${data.email}</p>

                <table border="1">
                    <tr>
                        <th>Product ID</th>
                        <th>Unit Price</th>
                        <th>Quantity</th>
                        <th>Tax</th>
                        <th>Total</th>
                    </tr>
            `;

            data.items.forEach(item => {
                html += `
                    <tr>
                        <td>${item.product_id}</td>
                        <td>${item.unit_price}</td>
                        <td>${item.quantity}</td>
                        <td>${item.tax}</td>
                        <td>${item.total}</td>
                    </tr>
                `;
            });

            html += `
                </table>

                <h3>Total Without Tax: ${data.total_without_tax}</h3>
                <h3>Total Tax: ${data.tax}</h3>
                <h3>Net Total: ${data.net_total}</h3>
                <h3>Balance: ${data.balance}</h3>
            `;

            document.getElementById("bill_content").innerHTML = html;
        });
};