Feature: Basic Flask page test

  Scenario: Visiting the homepage
    Given I open the homepage
    Then I should see "Welcome"