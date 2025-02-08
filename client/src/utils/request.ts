export async function request<T>(url: string, payload: object, method: string = 'POST'): Promise<T> {
    try {
        const response = await fetch(url, {
            method: method,
            body: JSON.stringify({
                ...payload,
                isPublic: true,
            }),
        });
        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

export async function poll<T>(
    action: () => Promise<T>,
    onSuccess?: (r) => void,
    isSuccess: (r) => boolean = (r) => (r.status === 'success'),
    interval: number = 1000,
    maxTimes: number = 40,
) {
    let counter = 0
    while (counter < maxTimes) {
        const result = await action()
        if (isSuccess(result)) {
            if (onSuccess) {
                onSuccess(result)
            }
            break;
        }
        counter++
        await new Promise(resolve => setTimeout(resolve, interval))
    }
    if (counter === maxTimes) {
        console.log('exceed max polling times, exit')
    }
}
