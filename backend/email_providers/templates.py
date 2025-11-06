from typing import Dict, Any, Optional, List
from string import Template
import logging

logger = logging.getLogger(__name__)


class EmailTemplateManager:
    """Provider-agnostic email template management"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load email templates"""
        return {
            "welcome": {
                "subject": "Welcome to ${app_name}!",
                "text": "Hi ${name},\n\nWelcome to ${app_name}! Get started: ${login_url}\n\nBest regards,\nThe ${app_name} Team",
                "html": "<h1>Welcome to ${app_name}!</h1><p>Hi ${name},</p><p><a href='${login_url}'>Get started</a></p>"
            },
            "password_reset": {
                "subject": "Reset Your Password",
                "text": "Hi ${name},\n\nReset your password: ${reset_url}\n\nExpires in 1 hour.\n\nBest regards,\nThe ${app_name} Team",
                "html": "<h1>Reset Password</h1><p>Hi ${name},</p><p><a href='${reset_url}'>Reset Password</a></p><p>Expires in 1 hour.</p>"
            },
            "email_verification": {
                "subject": "Verify Your Email Address",
                "text": "Hi ${name},\n\nVerify your email: ${verification_url}\n\nBest regards,\nThe ${app_name} Team",
                "html": "<h1>Verify Email</h1><p>Hi ${name},</p><p><a href='${verification_url}'>Verify Email</a></p>"
            },
            "subscription_created": {
                "subject": "Subscription Confirmed - ${plan_name}",
                "text": "Hi ${name},\n\n${plan_name} active! Price: ${price}\nNext billing: ${next_billing_date}\n\nView: ${dashboard_url}",
                "html": "<h1>Confirmed!</h1><p>Hi ${name},</p><p>${plan_name} active! ${price}</p><p><a href='${dashboard_url}'>View</a></p>"
            },
            "payment_failed": {
                "subject": "Payment Failed - Action Required",
                "text": "Hi ${name},\n\nPayment failed. Update payment method: ${billing_url}\n\nBest regards,\nThe ${app_name} Team",
                "html": "<h1 style='color:#dc3545;'>Payment Failed</h1><p>Hi ${name},</p><p><a href='${billing_url}'>Update Payment</a></p>"
            },
            "subscription_cancelled": {
                "subject": "Subscription Cancelled",
                "text": "Hi ${name},\n\nSubscription cancelled. Access until: ${end_date}\n\nReactivate: ${reactivate_url}",
                "html": "<h1>Cancelled</h1><p>Hi ${name},</p><p>Access until: ${end_date}</p><p><a href='${reactivate_url}'>Reactivate</a></p>"
            },
            "2fa_code": {
                "subject": "Your 2FA Code",
                "text": "Hi ${name},\n\nYour 2FA code: ${code}\n\nExpires in 5 minutes.",
                "html": "<h1>2FA Code</h1><p>Hi ${name},</p><h2 style='font-size:32px;letter-spacing:5px;'>${code}</h2><p>Expires in 5 minutes.</p>"
            }
        }
    
    def render(
        self,
        template_name: str,
        variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Render a template with variables.
        
        Args:
            template_name: Name of template
            variables: Variables to substitute
        
        Returns:
            Dict with 'subject', 'text', and 'html' keys
        """
        if template_name not in self.templates:
            logger.error(f"Template not found: {template_name}")
            raise ValueError(f"Template not found: {template_name}")
        
        template = self.templates[template_name]
        
        # Render each part
        rendered = {}
        for key in ['subject', 'text', 'html']:
            if key in template:
                t = Template(template[key])
                rendered[key] = t.safe_substitute(variables)
        
        return rendered
    
    def add_template(
        self,
        name: str,
        subject: str,
        text: str,
        html: Optional[str] = None
    ):
        """Add a new template"""
        self.templates[name] = {
            "subject": subject,
            "text": text
        }
        if html:
            self.templates[name]["html"] = html
        
        logger.info(f"Added email template: {name}")
    
    def list_templates(self) -> List[str]:
        """List available templates"""
        return list(self.templates.keys())

