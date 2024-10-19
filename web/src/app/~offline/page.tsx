import React from 'react';

const OfflinePage: React.FC = () => {
    return (
        <div style={styles.container}>
            <h1 style={styles.header}>Você está offline</h1>
            <p style={styles.message}>Verifique sua conexão com a internet e tente novamente.</p>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column' as 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        textAlign: 'center' as 'center',
        padding: '0 20px',
        backgroundColor: '#f8f9fa',
    },
    header: {
        fontSize: '2rem',
        marginBottom: '1rem',
    },
    message: {
        fontSize: '1rem',
    },
};

export default OfflinePage;
