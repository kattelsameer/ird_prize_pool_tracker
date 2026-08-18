import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import { WinnerCard } from "./WinnerCard";
import { renderWithProviders } from "../test/testUtils";
import { fixtureMatches } from "../test/fixtures";

describe("WinnerCard", () => {
  it("shows all three data-source labels (government, user, app) plus the claim disclaimer", () => {
    renderWithProviders(<WinnerCard match={fixtureMatches[0]} />);

    expect(screen.getByText(/IRD published data/i)).toBeInTheDocument();
    expect(screen.getByText(/Your entry/i)).toBeInTheDocument();
    expect(screen.getByText(/App-calculated/i)).toBeInTheDocument();

    // Never implies a guaranteed prize.
    expect(screen.getByText(/does not guarantee payment/i)).toBeInTheDocument();
    expect(screen.getByText(/original physical bill/i)).toBeInTheDocument();
  });

  it("shows the prize amount, net-after-tax amount, and winner rank", () => {
    renderWithProviders(<WinnerCard match={fixtureMatches[0]} />);

    expect(screen.getByText(/Rs 1,000,000/)).toBeInTheDocument();
    expect(screen.getByText(/Rs 750,000 after 25% tax/)).toBeInTheDocument();
    expect(screen.getByText(/Rank 1/)).toBeInTheDocument();
  });

  it("omits the amount line entirely when the category has no known prize tier", () => {
    const unknownAmountMatch = { ...fixtureMatches[0], prize_amount: null, prize_amount_net: null };
    renderWithProviders(<WinnerCard match={unknownAmountMatch} />);
    expect(screen.queryByText(/^Rs /)).not.toBeInTheDocument();
  });

  it("shows a fiscal-year-unconfirmed notice when applicable", () => {
    const unconfirmedMatch = { ...fixtureMatches[0], fiscal_year_unconfirmed: true };
    renderWithProviders(<WinnerCard match={unconfirmedMatch} />);
    expect(screen.getByRole("note")).toHaveTextContent(/haven't confirmed a fiscal year/i);
  });
});
