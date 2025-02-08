<template>
    <div class="loading-container">
        <div class="loader">
            <div class="dot dot1"></div>
            <div class="dot dot2"></div>
            <div class="dot dot3"></div>
        </div>
    </div>
</template>

<style>
.loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    font-family: "Arial", sans-serif;
    padding: 10px 0;
}

.loader {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #b4e7d2;
    margin: 5px;
    animation: bounce 0.8s infinite alternate;
}

@keyframes bounce {
    from {
        transform: translateY(0);
    }

    to {
        transform: translateY(-10px);
    }
}

.dot:nth-child(1) {
    animation-delay: 0.1s;
}

.dot:nth-child(2) {
    animation-delay: 0.2s;
}

.dot:nth-child(3) {
    animation-delay: 0.3s;
}

.loading-text {
    margin-top: 10px;
    font-size: 14px;
    color: #555;
}
</style>
