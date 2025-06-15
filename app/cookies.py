def click_cookie_button(driver):
    script = """
    const shadowHost = document.querySelector('#usercentrics-root');
    if (!shadowHost || !shadowHost.shadowRoot) return false;
    const acceptBtn = shadowHost.shadowRoot.querySelector('button[data-testid="uc-accept-all-button"]');
    if (acceptBtn) {
        acceptBtn.click();
        return true;
    }
    return false;
    """
    return driver.execute_script(script)