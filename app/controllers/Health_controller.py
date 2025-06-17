class HealthController: 
    """
    Health controller to manage health check endpoints."""
    def get_health():
        """
        Health check endpoint to verify the service is running.
        Returns a JSON response with the status.
        """
        return {"status": "ok"}